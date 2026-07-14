from __future__ import annotations

import logging
import os
import sys
from collections import deque
from datetime import datetime, timedelta, timezone
from pathlib import Path

from django.conf import settings
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from apps.detection.models import HashRecord, ProcessRecord, SecurityLog
from apps.monitoring.models import ProtectedFile
from feature_extraction.process_features import extract_process_features, find_processes_touching_path

logger = logging.getLogger(__name__)

DEFAULT_WATCH_PATHS = [
    Path(settings.BASE_DIR) / "demo_files",
]


def _configured_watch_paths() -> list[Path]:
    configured = getattr(settings, "CRDS_WATCH_PATHS", None)
    if configured:
        return [Path(path).resolve() for path in configured]
    paths = list(DEFAULT_WATCH_PATHS)
    for drive in getattr(settings, "CRDS_EXTRA_DRIVES", []):
        paths.append(Path(drive).resolve())
    return paths


class EndpointFileEventHandler(FileSystemEventHandler):
    """Captures filesystem events with process attribution and behavioral metadata."""

    def __init__(self):
        super().__init__()
        self.modification_window = deque()
        self.window_seconds = getattr(settings, "CRDS_FEATURE_WINDOW_SECONDS", 20)

    def _register_modification(self) -> int:
        now = datetime.now(timezone.utc)
        self.modification_window.append(now)
        cutoff = now - timedelta(seconds=self.window_seconds)
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
        resolved = Path(path).resolve()
        watch_roots = _configured_watch_paths()
        if any(str(resolved).startswith(str(root)) for root in watch_roots):
            return True
        return str(resolved) in self._tracked_paths()

    def _resolve_process(self, path: str) -> dict:
        processes = find_processes_touching_path(path)
        primary = processes[0] if processes else extract_process_features()
        return primary.to_dict()

    def _hash_flags(self, file_hash: str) -> tuple[bool, bool]:
        if not file_hash:
            return False, False
        record = HashRecord.objects.filter(sha256=file_hash).first()
        if not record:
            return False, False
        return record.label == "whitelist", record.label == "blacklist"

    def _log_event(self, event_type: str, path: str, action: str, message: str, previous_path: str = ""):
        if not self._should_track(path):
            return

        burst_count = self._register_modification()
        resolved_path = str(Path(path).resolve())
        process_data = self._resolve_process(resolved_path)

        import hashlib
        file_hash = ""
        file_path_obj = Path(resolved_path)
        if file_path_obj.is_file():
            try:
                digest = hashlib.sha256()
                with file_path_obj.open("rb") as handle:
                    digest.update(handle.read(8192))
                file_hash = digest.hexdigest()
            except OSError:
                file_hash = ""

        whitelist_hit, blacklist_hit = self._hash_flags(file_hash)

        from apps.detection.services.yara_scanner import scan_file
        yara_match, yara_rules = scan_file(resolved_path)

        payload = {
            "file_path": resolved_path,
            "previous_path": previous_path,
            "file_mod_count": burst_count,
            "window_seconds": self.window_seconds,
            "files_accessed_count": burst_count,
            "process_known": process_data.get("process_reputation", 0.5) >= 0.6,
            "process_name": process_data.get("process_name"),
            "executable_path": process_data.get("executable_path"),
            "pid": process_data.get("pid"),
            "parent_pid": process_data.get("parent_pid"),
            "parent_name": process_data.get("parent_name"),
            "cmdline": process_data.get("cmdline"),
            "username": process_data.get("username"),
            "content_modified": action == "modify",
            "event_action": action,
            "file_hash_sha256": file_hash,
            "whitelist_hit": whitelist_hit,
            "blacklist_hit": blacklist_hit,
            "yara_match": yara_match,
            "yara_rules": yara_rules,
            "has_ransom_note": file_path_obj.name.upper() == "README.TXT" and action == "create",
        }

        log = SecurityLog.objects.create(
            source="monitoring",
            event_type=event_type,
            action=action,
            file_path=resolved_path,
            message=message,
            metadata=payload,
        )

        ProcessRecord.objects.create(
            security_log=log,
            pid=int(process_data.get("pid") or 0),
            process_name=process_data.get("process_name", ""),
            executable_path=process_data.get("executable_path", ""),
            username=process_data.get("username", ""),
            parent_pid=int(process_data.get("parent_pid") or 0),
            cmdline=process_data.get("cmdline", ""),
            metadata=process_data,
        )

        logger.info("[MONITOR] %s/%s: %s (log_id=%s pid=%s)", event_type, action, path, log.id, process_data.get("pid"))

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
            self._log_event(
                "file_event",
                event.dest_path,
                "rename",
                f"File renamed from {event.src_path}",
                previous_path=event.src_path,
            )


class EndpointFileMonitor:
    """Manages recursive watchdog observers for configured paths."""

    def __init__(self):
        self.observer: Observer | None = None
        self.handler = EndpointFileEventHandler()

    def start(self):
        if self.observer and self.observer.is_alive():
            return

        self.observer = Observer()
        watch_dirs: set[str] = set()

        for directory in _configured_watch_paths():
            directory.mkdir(parents=True, exist_ok=True)
            watch_dirs.add(str(directory))

        for row in ProtectedFile.objects.all().only("file_path"):
            watch_dirs.add(str(Path(row.file_path).resolve().parent))

        recursive = getattr(settings, "CRDS_RECURSIVE_MONITORING", True)
        for directory in sorted(watch_dirs):
            Path(directory).mkdir(parents=True, exist_ok=True)
            self.observer.schedule(self.handler, directory, recursive=recursive)

        self.observer.start()
        logger.info("[MONITOR] Endpoint monitoring started (recursive=%s)", recursive)
        logger.info("[MONITOR] Watch targets: %s", sorted(watch_dirs))

    def stop(self):
        if not self.observer:
            return
        self.observer.stop()
        self.observer.join(timeout=5)
        self.observer = None
        logger.info("[MONITOR] Endpoint monitoring stopped")

    def is_running(self) -> bool:
        return bool(self.observer and self.observer.is_alive())


# Backward-compatible aliases
DemoFileEventHandler = EndpointFileEventHandler
DemoFileMonitor = EndpointFileMonitor
