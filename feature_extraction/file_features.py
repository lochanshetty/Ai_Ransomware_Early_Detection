from __future__ import annotations

import hashlib
import time
from collections import deque
from dataclasses import dataclass, asdict, field
from pathlib import Path

from feature_extraction.entropy import file_entropy


RANSOM_EXTENSIONS = {
    ".locked", ".encrypted", ".enc", ".crypt", ".crypto", ".ryuk",
    ".wannacry", ".cerber", ".locky", ".zzzzz",
}


@dataclass
class FileEventContext:
    file_path: str = ""
    action: str = ""
    previous_path: str = ""
    event_timestamp: float = field(default_factory=time.time)


@dataclass
class FileFeatures:
    file_mod_count: float = 0.0
    files_accessed_count: float = 0.0
    files_modified_per_second: float = 0.0
    rename_ratio: float = 0.0
    extension_changed: float = 0.0
    entropy: float = 0.0
    entropy_delta: float = 0.0
    avg_file_size_modified: float = 0.0
    directory_traversal_speed: float = 0.0
    read_write_ratio: float = 1.0
    shannon_entropy: float = 0.0
    file_hash_sha256: str = ""
    sequence_length: float = 0.0
    time_between_actions_ms: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)


class FileEventWindow:
    """Rolling window tracker for filesystem behavioral metrics."""

    def __init__(self, window_seconds: float = 20.0):
        self.window_seconds = window_seconds
        self._events: deque[FileEventContext] = deque()
        self._entropy_cache: dict[str, float] = {}

    def _prune(self, now: float) -> None:
        cutoff = now - self.window_seconds
        while self._events and self._events[0].event_timestamp < cutoff:
            self._events.popleft()

    def record(self, context: FileEventContext) -> FileFeatures:
        now = context.event_timestamp or time.time()
        self._prune(now)
        self._events.append(context)

        actions = [event.action for event in self._events]
        paths = [event.file_path for event in self._events]
        mod_count = sum(1 for action in actions if action in {"modify", "rename", "create"})
        rename_count = sum(1 for action in actions if action == "rename")
        elapsed = max(now - self._events[0].event_timestamp, 0.001) if self._events else 1.0

        unique_dirs = len({str(Path(path).parent) for path in paths if path})
        prev_entropy = self._entropy_cache.get(context.file_path, 0.0)
        current_entropy = file_entropy(context.file_path) if context.file_path and Path(context.file_path).is_file() else 0.0
        if context.file_path:
            self._entropy_cache[context.file_path] = current_entropy

        extension_changed = 0.0
        if context.action == "rename" and context.previous_path:
            old_ext = Path(context.previous_path).suffix.lower()
            new_ext = Path(context.file_path).suffix.lower()
            if old_ext != new_ext or new_ext in RANSOM_EXTENSIONS:
                extension_changed = 1.0

        file_size = 0.0
        if context.file_path and Path(context.file_path).is_file():
            try:
                file_size = float(Path(context.file_path).stat().st_size)
            except OSError:
                file_size = 0.0

        file_hash = ""
        if context.file_path and Path(context.file_path).is_file():
            try:
                digest = hashlib.sha256()
                with Path(context.file_path).open("rb") as handle:
                    digest.update(handle.read(8192))
                file_hash = digest.hexdigest()
            except OSError:
                file_hash = ""

        time_between = 0.0
        if len(self._events) >= 2:
            time_between = (self._events[-1].event_timestamp - self._events[-2].event_timestamp) * 1000.0

        return FileFeatures(
            file_mod_count=float(mod_count),
            files_accessed_count=float(len(set(paths))),
            files_modified_per_second=float(mod_count / elapsed),
            rename_ratio=float(rename_count / max(len(actions), 1)),
            extension_changed=extension_changed,
            entropy=current_entropy,
            entropy_delta=max(0.0, current_entropy - prev_entropy),
            avg_file_size_modified=file_size,
            directory_traversal_speed=float(unique_dirs / elapsed),
            read_write_ratio=1.0,
            shannon_entropy=current_entropy,
            file_hash_sha256=file_hash,
            sequence_length=float(len(self._events)),
            time_between_actions_ms=time_between,
        )
