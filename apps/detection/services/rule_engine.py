from apps.detection.models import SecurityLog, ThreatLevel


def heuristic_assessment(log: SecurityLog) -> tuple[bool, ThreatLevel, str]:
    """
    Rule-based checks for ransomware-like behavior using extracted metadata.
    """

    metadata = log.metadata or {}
    file_mod_count = int(metadata.get("file_mod_count", 0))
    window_seconds = int(metadata.get("window_seconds", 60))
    files_accessed_count = int(metadata.get("files_accessed_count", 0))
    process_known = bool(metadata.get("process_known", True))
    mod_rate = float(metadata.get("files_modified_per_second", 0))
    entropy_delta = float(metadata.get("entropy_delta", 0))

    if file_mod_count >= 5 and window_seconds <= 15:
        return True, ThreatLevel.HIGH, "Burst file modifications detected"

    if mod_rate >= 3.0:
        return True, ThreatLevel.HIGH, f"High encryption/modification rate ({mod_rate:.1f}/s)"

    if entropy_delta >= 3.0:
        return True, ThreatLevel.HIGH, f"Large entropy increase (+{entropy_delta:.1f})"

    if not process_known and files_accessed_count >= 8:
        return True, ThreatLevel.HIGH, "Unknown process accessed many files"

    if file_mod_count >= 3 and window_seconds <= 30:
        return True, ThreatLevel.MEDIUM, "Elevated file modification pattern"

    return False, ThreatLevel.LOW, "No suspicious rule hit"
