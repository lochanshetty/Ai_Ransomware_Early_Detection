from __future__ import annotations

from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings

DEMO_DIR = Path(settings.BASE_DIR) / "demo_files"
KEY_FILE = DEMO_DIR / ".demo_fernet.key"


def _ensure_demo_path(file_path: Path) -> Path:
    resolved = file_path.resolve()
    demo_root = DEMO_DIR.resolve()
    if not str(resolved).startswith(str(demo_root)):
        raise ValueError("Encryption is restricted to demo_files for safety.")
    return resolved


def _get_cipher() -> Fernet:
    DEMO_DIR.mkdir(parents=True, exist_ok=True)
    if not KEY_FILE.exists():
        KEY_FILE.write_bytes(Fernet.generate_key())
    return Fernet(KEY_FILE.read_bytes())


def encrypt_file(file_path: str) -> str:
    """
    Encrypts file bytes using Fernet and renames file with .locked suffix.
    """

    src = _ensure_demo_path(Path(file_path))
    if src.name.endswith(".locked"):
        return str(src)

    payload = src.read_bytes()
    encrypted = _get_cipher().encrypt(payload)
    src.write_bytes(encrypted)

    locked = src.with_name(f"{src.name}.locked")
    src.rename(locked)
    print(f"[SIM] File encrypted using AES: {locked.name}")
    return str(locked)


def decrypt_file(file_path: str) -> str:
    """
    Decrypts a previously encrypted .locked file and restores original name.
    """

    locked = _ensure_demo_path(Path(file_path))
    if not locked.name.endswith(".locked"):
        return str(locked)

    encrypted = locked.read_bytes()
    try:
        decrypted = _get_cipher().decrypt(encrypted)
    except InvalidToken as exc:
        raise ValueError(f"Unable to decrypt file: {locked}") from exc

    restored = locked.with_name(locked.name[:-7])
    locked.write_bytes(decrypted)
    locked.rename(restored)
    return str(restored)
