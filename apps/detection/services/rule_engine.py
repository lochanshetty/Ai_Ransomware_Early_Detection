from apps.detection.models import SecurityLog, ThreatLevel


def heuristic_assessment(log: SecurityLog) -> tuple[bool, ThreatLevel, str]:
    """
    Rule-based checks for ransomware-like behavior.

    - Too many file modifications in short time.
    - Unknown process accessing many files.
    """

    metadata = log.metadata or {}
    file_mod_count = int(metadata.get("file_mod_count", 0))
    window_seconds = int(metadata.get("window_seconds", 60))
    files_accessed_count = int(metadata.get("files_accessed_count", 0))
    process_known = bool(metadata.get("process_known", True))

    # Demo-tuned threshold: frequent changes in a short window imply ransomware-like behavior.
    if file_mod_count >= 5 and window_seconds <= 15:
        return True, ThreatLevel.HIGH, "Burst file modifications detected"

    if not process_known and files_accessed_count >= 8:
        return True, ThreatLevel.HIGH, "Unknown process accessed many files"

    if file_mod_count >= 3 and window_seconds <= 30:
        return True, ThreatLevel.MEDIUM, "Elevated file modification pattern"

    return False, ThreatLevel.LOW, "No suspicious rule hit"
