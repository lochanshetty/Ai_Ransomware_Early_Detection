from __future__ import annotations

from collections import deque
from datetime import datetime, timedelta, timezone
from pathlib import Path

from django.conf import settings
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from apps.detection.models import SecurityLog
from apps.monitoring.models import ProtectedFile

DEMO_DIR = Path(settings.BASE_DIR) / "demo_files"


class DemoFileEventHandler(FileSystemEventHandler):
    """Captures filesystem events from demo_files and protected registry files."""

    def __init__(self):
        super().__init__()
        self.modification_window = deque()

    def _register_modification(self):
        now = datetime.now(timezone.utc)
        self.modification_window.append(now)
        cutoff = now - timedelta(seconds=15)
        while self.modification_window and self.modification_window[0] < cutoff:
            self.modification_window.popleft()
        return len(self.modification_window)

    def _tracked_paths(self) -> set[str]:
        protected = {
            str(Path(row.file_path).resolve())
            for row in ProtectedFile.objects.all().only("file_path")
        }
        return protected

    def _should_track(self, path: str) -> bool:
        resolved = str(Path(path).resolve())
        if resolved.startswith(str(DEMO_DIR.resolve())):
            return True
        return resolved in self._tracked_paths()

    def _log_event(self, event_type: str, path: str, action: str, message: str):
        if not self._should_track(path):
            return

        burst_count = self._register_modification()
        resolved_path = str(Path(path).resolve())
        payload = {
            "file_path": resolved_path,
            "file_mod_count": burst_count,
            "window_seconds": 15,
            "files_accessed_count": burst_count,
            "process_known": False,
            "process_name": "demo_simulation",
            "content_modified": action == "modify",
            "event_action": action,
        }
        log = SecurityLog.objects.create(
            source="monitoring",
            event_type=event_type,
            action=action,
            file_path=resolved_path,
            message=message,
            metadata=payload,
        )
        print(f"[MONITOR] {event_type}/{action}: {path} (log_id={log.id})")

    def on_created(self, event):
        if not event.is_directory:
            self._log_event("file_event", event.src_path, "create", "File created")

    def on_modified(self, event):
        if not event.is_directory:
            self._log_event("file_event", event.src_path, "modify", "File modified")

    def on_deleted(self, event):
        if not event.is_directory:
            self._log_event("file_event", event.src_path, "delete", "File deleted")

    def on_moved(self, event):
        if not event.is_directory:
            self._log_event("file_event", event.dest_path, "rename", f"File renamed from {event.src_path}")


class DemoFileMonitor:
    """Manages watchdog observer lifecycle for demo_files and protected registry."""

    def __init__(self):
        self.observer: Observer | None = None
        self.handler = DemoFileEventHandler()

    def start(self):
        if self.observer and self.observer.is_alive():
            return

        DEMO_DIR.mkdir(parents=True, exist_ok=True)
        self.observer = Observer()
        watch_dirs = {str(DEMO_DIR.resolve())}
        for row in ProtectedFile.objects.all().only("file_path"):
            watch_dirs.add(str(Path(row.file_path).resolve().parent))

        for directory in watch_dirs:
            Path(directory).mkdir(parents=True, exist_ok=True)
            self.observer.schedule(self.handler, directory, recursive=False)

        self.observer.start()
        print("[MONITOR] Monitoring started...")
        print(f"[MONITOR] Watch targets: {sorted(watch_dirs)}")

    def stop(self):
        if not self.observer:
            return
        self.observer.stop()
        self.observer.join(timeout=2)
        self.observer = None

    def is_running(self) -> bool:
        return bool(self.observer and self.observer.is_alive())
