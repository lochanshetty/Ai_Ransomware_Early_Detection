"""
CRDS safe ransomware simulation demo.

How to run:
1) Start backend: python manage.py runserver
2) Start monitoring: POST http://127.0.0.1:8000/monitor/start
3) Run this script: python simulate_attack.py
4) View logs: GET http://127.0.0.1:8000/monitor/logs
5) View threats: GET http://127.0.0.1:8000/detect/threats

This script is safe:
- It does NOT encrypt files.
- It only renames files by appending ".locked".
"""

from pathlib import Path
from time import sleep
import argparse

from utils.encryption import encrypt_file

DEMO_DIR = Path(__file__).resolve().parent / "demo_files"


def simulate(with_note: bool = False):
    print("[SIM] Simulating ransomware...")
    if not DEMO_DIR.exists():
        print(f"[SIM] demo_files not found at {DEMO_DIR}")
        return

    files = [
        path for path in DEMO_DIR.iterdir()
        if path.is_file() and not path.name.endswith(".locked") and not path.name.startswith(".demo_fernet")
    ]
    if not files:
        print("[SIM] No eligible files found (already renamed or missing).")
        return

    for file_path in files:
        locked_path = Path(encrypt_file(str(file_path)))
        print(f"[SIM] Encrypted+Renamed: {file_path.name} -> {locked_path.name}")
        sleep(0.5)

    if with_note:
        note_path = DEMO_DIR / "README.txt"
        note_path.write_text(
            "Your files are locked. This is a safe CRDS demo note.\n",
            encoding="utf-8",
        )
        print(f"[SIM] Created ransom-note simulation: {note_path.name}")

    print("[SIM] Demo simulation complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Safe CRDS ransomware activity simulator")
    parser.add_argument(
        "--with-note",
        action="store_true",
        help="Create README.txt ransom-note simulation for Generic classification",
    )
    args = parser.parse_args()
    simulate(with_note=args.with_note)
