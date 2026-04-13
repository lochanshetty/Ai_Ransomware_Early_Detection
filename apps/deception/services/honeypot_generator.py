import random
from pathlib import Path

from apps.deception.models import HoneypotFile

SENSITIVE_KEYWORDS = (
    "bank_statement",
    "passwords",
    "confidential",
    "salary_sheet",
    "finance_report",
)

FILE_EXTENSIONS = (".txt", ".csv", ".xlsx", ".docx")


def _build_filename() -> str:
    keyword = random.choice(SENSITIVE_KEYWORDS)
    suffix = random.randint(100, 999)
    extension = random.choice(FILE_EXTENSIONS)
    return f"{keyword}_{suffix}{extension}"


def create_honeypot_files(monitored_directories: list[str], count: int = 5) -> list[HoneypotFile]:
    """
    Safely creates decoy files inside monitored directories.

    Files only contain inert text markers and do not execute any code.
    """

    if not monitored_directories:
        return []

    created_records = []
    for _ in range(max(count, 1)):
        directory = Path(random.choice(monitored_directories))
        directory.mkdir(parents=True, exist_ok=True)
        file_path = directory / _build_filename()
        file_path.write_text(
            "CRDS honeypot file. Unauthorized access is monitored.\n",
            encoding="utf-8",
        )

        record, _ = HoneypotFile.objects.get_or_create(file_path=str(file_path.resolve()))
        created_records.append(record)

    return created_records
