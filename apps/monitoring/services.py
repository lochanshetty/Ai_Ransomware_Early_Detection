import uuid
from datetime import datetime, timezone


class MonitorRuntimeState:
    """Keeps lightweight in-process monitoring runtime state for phase 1."""

    def __init__(self):
        self.is_running = False
        self.run_id = None
        self.started_at = None

    def start(self) -> str:
        self.is_running = True
        self.run_id = str(uuid.uuid4())
        self.started_at = datetime.now(timezone.utc)
        return self.run_id

    def status(self) -> dict:
        return {
            "is_running": self.is_running,
            "run_id": self.run_id,
            "started_at": self.started_at.isoformat() if self.started_at else None,
        }


# Singleton service instance used by API views.
monitor_runtime = MonitorRuntimeState()
