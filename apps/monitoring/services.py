import uuid
from datetime import datetime, timezone
import threading

from apps.monitoring.file_monitor import DemoFileMonitor
from simulate_attack import run_attack_loop


class MonitorRuntimeState:
    """Keeps lightweight in-process monitoring runtime state for phase 1."""

    def __init__(self):
        self.is_running = False
        self.run_id = None
        self.started_at = None
        self.file_monitor = DemoFileMonitor()
        self.attack_status = "stopped"
        self.attack_running = False
        self.attack_thread: threading.Thread | None = None

    def start(self) -> str:
        self.file_monitor.start()
        self.is_running = True
        self.run_id = str(uuid.uuid4())
        self.started_at = datetime.now(timezone.utc)
        return self.run_id

    def stop(self):
        self.file_monitor.stop()
        self.is_running = False

    def restart(self):
        """Reloads watch targets (used when registry files are added)."""

        self.file_monitor.stop()
        self.file_monitor.start()

    def status(self) -> dict:
        return {
            "is_running": self.file_monitor.is_running(),
            "run_id": self.run_id,
            "started_at": self.started_at.isoformat() if self.started_at else None,
        }

    def run_attack(self):
        if self.attack_running:
            return
        self.start()
        self.attack_running = True
        self.attack_thread = threading.Thread(
            target=run_attack_loop,
            args=(lambda: self.attack_running,),
            kwargs={"with_note": True},
            daemon=True,
        )
        self.attack_thread.start()
        self.attack_status = "running"

    def stop_attack(self):
        self.attack_running = False
        if self.attack_thread and self.attack_thread.is_alive():
            self.attack_thread.join(timeout=4)
        self.attack_thread = None
        self.attack_status = "stopped"

    def system_state(self) -> dict:
        monitoring = "running" if self.file_monitor.is_running() else "stopped"
        return {
            "monitoring": monitoring,
            "attack": self.attack_status,
        }


# Singleton service instance used by API views.
monitor_runtime = MonitorRuntimeState()
