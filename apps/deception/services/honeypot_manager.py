from apps.deception.models import HoneypotFile
from apps.deception.services.honeypot_generator import generate_honeypots


def create_honeypot_files(base_directory: str | None = None) -> list[HoneypotFile]:
    """
    Backward-compatible wrapper for legacy imports.
    """

    return generate_honeypots()
