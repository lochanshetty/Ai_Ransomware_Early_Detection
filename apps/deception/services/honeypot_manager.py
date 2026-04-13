from pathlib import Path

from django.conf import settings

from apps.deception.models import HoneypotFile


DEFAULT_HONEYPOT_FILES = (
    "finance/payroll_2026.xlsx",
    "legal/client_contracts_q2.docx",
    "credentials/server_root_passwords.txt",
    "hr/employee_ssn_dump.csv",
)


def create_honeypot_files(base_directory: str | None = None) -> list[HoneypotFile]:
    """
    Creates fake sensitive files and persists them in honeypot registry.

    Returns a list of active HoneypotFile records.
    """

    root = Path(base_directory) if base_directory else Path(settings.BASE_DIR) / "honeypots"
    root.mkdir(parents=True, exist_ok=True)

    created_or_existing = []
    for relative in DEFAULT_HONEYPOT_FILES:
        target_file = root / relative
        target_file.parent.mkdir(parents=True, exist_ok=True)

        if not target_file.exists():
            target_file.write_text(
                "CRDS honeypot file. Unauthorized access is monitored.\n",
                encoding="utf-8",
            )

        record, _ = HoneypotFile.objects.get_or_create(
            file_path=str(target_file.resolve()),
            defaults={
                "display_name": target_file.name,
                "is_active": True,
            },
        )
        if not record.is_active:
            record.is_active = True
            record.save(update_fields=["is_active"])
        created_or_existing.append(record)

    return created_or_existing
