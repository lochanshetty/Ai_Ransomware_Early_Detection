from __future__ import annotations

from dataclasses import dataclass, asdict, field

from feature_extraction.file_features import FileEventContext, FileEventWindow, FileFeatures
from feature_extraction.process_features import ProcessFeatures, extract_process_features, find_processes_touching_path
from feature_extraction.system_features import SystemFeatures, extract_system_features


FEATURE_NAMES = [
    "file_mod_count",
    "files_accessed_count",
    "files_modified_per_second",
    "rename_ratio",
    "extension_changed",
    "entropy",
    "entropy_delta",
    "avg_file_size_modified",
    "directory_traversal_speed",
    "shannon_entropy",
    "sequence_length",
    "time_between_actions_ms",
    "process_reputation",
    "cpu_percent",
    "memory_percent",
    "num_threads",
    "parent_pid",
    "system_cpu_percent",
    "system_memory_percent",
    "disk_write_bytes",
    "process_known",
    "yara_match",
    "honeypot_hit",
    "blacklist_hit",
]


@dataclass
class FeatureVector:
    names: list[str] = field(default_factory=lambda: list(FEATURE_NAMES))
    values: list[float] = field(default_factory=list)
    file_features: dict = field(default_factory=dict)
    process_features: dict = field(default_factory=dict)
    system_features: dict = field(default_factory=dict)
    extras: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "names": self.names,
            "values": self.values,
            "file_features": self.file_features,
            "process_features": self.process_features,
            "system_features": self.system_features,
            "extras": self.extras,
        }

    def as_array(self) -> list[float]:
        if not self.values:
            self.values = [0.0] * len(self.names)
        return self.values


class FeatureAggregator:
    """Combines file, process, and system features into a model-ready vector."""

    def __init__(self, window_seconds: float = 20.0):
        self._file_window = FileEventWindow(window_seconds=window_seconds)

    def build(
        self,
        *,
        file_path: str,
        action: str,
        previous_path: str = "",
        pid: int | None = None,
        process_known: bool = True,
        yara_match: bool = False,
        honeypot_hit: bool = False,
        blacklist_hit: bool = False,
    ) -> FeatureVector:
        file_ctx = FileEventContext(
            file_path=file_path,
            action=action,
            previous_path=previous_path,
        )
        file_feats: FileFeatures = self._file_window.record(file_ctx)

        process_feats: ProcessFeatures
        if pid:
            process_feats = extract_process_features(pid)
        elif file_path:
            processes = find_processes_touching_path(file_path)
            process_feats = processes[0]
        else:
            process_feats = extract_process_features()

        system_feats: SystemFeatures = extract_system_features()

        values = [
            file_feats.file_mod_count,
            file_feats.files_accessed_count,
            file_feats.files_modified_per_second,
            file_feats.rename_ratio,
            file_feats.extension_changed,
            file_feats.entropy,
            file_feats.entropy_delta,
            file_feats.avg_file_size_modified,
            file_feats.directory_traversal_speed,
            file_feats.shannon_entropy,
            file_feats.sequence_length,
            file_feats.time_between_actions_ms,
            process_feats.process_reputation,
            process_feats.cpu_percent,
            process_feats.memory_percent,
            float(process_feats.num_threads),
            float(process_feats.parent_pid),
            system_feats.cpu_percent,
            system_feats.memory_percent,
            float(system_feats.disk_write_bytes),
            0.0 if process_known else 1.0,
            1.0 if yara_match else 0.0,
            1.0 if honeypot_hit else 0.0,
            1.0 if blacklist_hit else 0.0,
        ]

        return FeatureVector(
            values=values,
            file_features=file_feats.to_dict(),
            process_features=process_feats.to_dict(),
            system_features=system_feats.to_dict(),
            extras={
                "file_path": file_path,
                "action": action,
                "file_hash_sha256": file_feats.file_hash_sha256,
            },
        )
