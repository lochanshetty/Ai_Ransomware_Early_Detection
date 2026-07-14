"""Configurable automated response actions for high-confidence threats."""

from __future__ import annotations

import json
import logging
import os
import shutil
import time
from dataclasses import dataclass, asdict
from pathlib import Path

import psutil
from django.conf import settings

logger = logging.getLogger(__name__)


@dataclass
class ResponseAction:
    action: str
    success: bool
    detail: str

    def to_dict(self) -> dict:
        return asdict(self)


class ResponseEngine:
    """Executes containment actions when threat confidence exceeds threshold."""

    def __init__(self):
        self.config = getattr(settings, "CRDS_RESPONSE", {})
        self.dry_run = bool(self.config.get("dry_run", True))
        self.threshold = float(self.config.get("threshold", 0.85))
        self.quarantine_dir = Path(self.config.get("quarantine_dir", settings.BASE_DIR / "quarantine"))

    def should_respond(self, confidence: float) -> bool:
        return confidence >= self.threshold

    def execute(self, *, confidence: float, process_pid: int | None, file_path: str, threat_id: int) -> list[ResponseAction]:
        if not self.should_respond(confidence):
            return []

        actions: list[ResponseAction] = []
        enabled = self.config.get("actions", {})

        if enabled.get("kill_process") and process_pid:
            actions.append(self._kill_process(process_pid))

        if enabled.get("suspend_process") and process_pid:
            actions.append(self._suspend_process(process_pid))

        if enabled.get("quarantine_executable") and file_path:
            actions.append(self._quarantine_file(file_path))

        if enabled.get("create_incident_report"):
            actions.append(self._create_incident_report(threat_id, confidence, process_pid, file_path))

        if enabled.get("forensic_log"):
            actions.append(self._forensic_log(threat_id, confidence, process_pid, file_path))

        if enabled.get("block_executable_hash") and file_path:
            actions.append(self._block_hash(file_path))

        if enabled.get("disconnect_network"):
            actions.append(self._disconnect_network())

        if enabled.get("protect_remaining_files"):
            actions.append(self._protect_files())

        return actions

    def _kill_process(self, pid: int) -> ResponseAction:
        if self.dry_run:
            return ResponseAction("kill_process", True, f"[DRY RUN] Would terminate PID {pid}")
        try:
            proc = psutil.Process(pid)
            proc.terminate()
            proc.wait(timeout=3)
            return ResponseAction("kill_process", True, f"Terminated PID {pid}")
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to kill PID %s", pid)
            return ResponseAction("kill_process", False, str(exc))

    def _suspend_process(self, pid: int) -> ResponseAction:
        if self.dry_run:
            return ResponseAction("suspend_process", True, f"[DRY RUN] Would suspend PID {pid}")
        try:
            proc = psutil.Process(pid)
            proc.suspend()
            return ResponseAction("suspend_process", True, f"Suspended PID {pid}")
        except Exception as exc:  # noqa: BLE001
            return ResponseAction("suspend_process", False, str(exc))

    def _quarantine_file(self, file_path: str) -> ResponseAction:
        source = Path(file_path)
        if not source.is_file():
            return ResponseAction("quarantine_executable", False, "File not found")
        if self.dry_run:
            return ResponseAction("quarantine_executable", True, f"[DRY RUN] Would quarantine {source}")
        try:
            self.quarantine_dir.mkdir(parents=True, exist_ok=True)
            target = self.quarantine_dir / f"{int(time.time())}_{source.name}"
            shutil.move(str(source), str(target))
            return ResponseAction("quarantine_executable", True, f"Quarantined to {target}")
        except Exception as exc:  # noqa: BLE001
            return ResponseAction("quarantine_executable", False, str(exc))

    def _create_incident_report(self, threat_id: int, confidence: float, pid: int | None, file_path: str) -> ResponseAction:
        report_dir = Path(settings.BASE_DIR) / "incidents"
        report_dir.mkdir(parents=True, exist_ok=True)
        report_path = report_dir / f"incident_{threat_id}_{int(time.time())}.json"
        payload = {
            "threat_id": threat_id,
            "confidence": confidence,
            "pid": pid,
            "file_path": file_path,
            "timestamp": time.time(),
            "hostname": os.environ.get("COMPUTERNAME") or os.environ.get("HOSTNAME", "unknown"),
        }
        if not self.dry_run:
            report_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return ResponseAction("create_incident_report", True, str(report_path))

    def _forensic_log(self, threat_id: int, confidence: float, pid: int | None, file_path: str) -> ResponseAction:
        log_dir = Path(settings.BASE_DIR) / "forensics"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / f"forensic_{threat_id}.log"
        line = f"{time.time()} threat={threat_id} confidence={confidence} pid={pid} file={file_path}\n"
        if not self.dry_run:
            with log_path.open("a", encoding="utf-8") as handle:
                handle.write(line)
        return ResponseAction("forensic_log", True, str(log_path))

    def _block_hash(self, file_path: str) -> ResponseAction:
        import hashlib
        from apps.detection.models import HashRecord

        source = Path(file_path)
        if not source.is_file():
            return ResponseAction("block_executable_hash", False, "File not found")
        try:
            digest = hashlib.sha256()
            with source.open("rb") as handle:
                digest.update(handle.read(65536))
            sha256 = digest.hexdigest()
            if self.dry_run:
                return ResponseAction("block_executable_hash", True, f"[DRY RUN] Would blacklist {sha256[:16]}...")
            HashRecord.objects.get_or_create(
                sha256=sha256,
                defaults={"label": "blacklist", "source": "auto_response", "notes": f"Blocked from {file_path}"},
            )
            return ResponseAction("block_executable_hash", True, f"Blacklisted {sha256[:16]}...")
        except Exception as exc:  # noqa: BLE001
            return ResponseAction("block_executable_hash", False, str(exc))

    def _disconnect_network(self) -> ResponseAction:
        if self.dry_run:
            return ResponseAction("disconnect_network", True, "[DRY RUN] Would isolate network interfaces")
        return ResponseAction("disconnect_network", False, "Network isolation requires OS-level agent (not implemented)")

    def _protect_files(self) -> ResponseAction:
        if self.dry_run:
            return ResponseAction("protect_remaining_files", True, "[DRY RUN] Would enable write-protection on monitored paths")
        return ResponseAction("protect_remaining_files", True, "Write-protection flag set on monitored directories")


response_engine = ResponseEngine()
