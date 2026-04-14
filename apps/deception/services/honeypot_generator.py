from pathlib import Path

from django.conf import settings

from apps.deception.models import HoneypotFile

DEFAULT_HONEYPOTS = (
    "passwords.txt",
    "bank_details.xlsx",
    "confidential_data.txt",
)


def generate_honeypots() -> list[HoneypotFile]:
    """
    Creates deterministic honeypot files in demo_files and stores them in DB.
    """

    demo_dir = Path(settings.BASE_DIR) / "demo_files"
    demo_dir.mkdir(parents=True, exist_ok=True)

    created_records: list[HoneypotFile] = []
    for file_name in DEFAULT_HONEYPOTS:
        file_path = demo_dir / file_name
        if not file_path.exists():
            file_path.write_text(
                "CRDS honeypot file. Unauthorized access is monitored.\n",
                encoding="utf-8",
            )
            print(f"[DECEPTION] Honeypot created: {file_path.name}")

        record, _ = HoneypotFile.objects.get_or_create(
            file_path=str(file_path.resolve()),
        )
        created_records.append(record)

    return created_records


def create_honeypot_files(monitored_directories: list[str] | None = None, count: int = 5) -> list[HoneypotFile]:
    """
    Backward-compatible wrapper for existing imports.
    """

    return generate_honeypots()
