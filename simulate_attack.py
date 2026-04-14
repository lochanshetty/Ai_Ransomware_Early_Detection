"""
CRDS safe ransomware simulation demo.

How to run:
1) Start backend: python manage.py runserver
2) Start monitoring: POST http://127.0.0.1:8000/monitor/start
3) Run this script: python simulate_attack.py
4) View logs: GET http://127.0.0.1:8000/monitor/logs
5) View threats: GET http://127.0.0.1:8000/detect/threats

This script is safe:
- It uses reversible Fernet-based encryption for demo files only.
- It renames encrypted files by appending ".locked".
"""

from pathlib import Path
from time import sleep
import argparse

from utils.encryption import encrypt_file

DEMO_DIR = Path(__file__).resolve().parent / "demo_files"


def simulate_once(with_note: bool = False) -> int:
    print("[SIM] Simulating ransomware...")
    if not DEMO_DIR.exists():
        print(f"[SIM] demo_files not found at {DEMO_DIR}")
        return 0

    files = [
        path for path in DEMO_DIR.iterdir()
        if path.is_file() and not path.name.endswith(".locked") and not path.name.startswith(".demo_fernet")
    ]
    if not files:
        print("[SIM] No eligible files found (already encrypted).")
        return 0

    encrypted_count = 0
    for file_path in files:
        locked_path = Path(encrypt_file(str(file_path)))
        print(f"[SIM] Encrypted+Renamed: {file_path.name} -> {locked_path.name}")
        encrypted_count += 1
        sleep(0.5)

    if with_note:
        note_path = DEMO_DIR / "README.txt"
        note_path.write_text(
            "Your files are locked. This is a safe CRDS demo note.\n",
            encoding="utf-8",
        )
        print(f"[SIM] Created ransom-note simulation: {note_path.name}")

    print("[SIM] Demo simulation complete.")
    return encrypted_count


def run_attack_loop(should_continue, with_note: bool = False):
    """
    Runs simulation continuously until caller-provided flag returns False.
    """

    print("[SIM] Continuous attack loop started")
    while should_continue():
        try:
            changed = simulate_once(with_note=with_note)
        except Exception as exc:  # noqa: BLE001
            print(f"[SIM] Loop iteration error: {exc}")
            changed = 0
        if changed == 0:
            # Keep attack alive and observable without destructive behavior.
            heartbeat = DEMO_DIR / "attack_heartbeat.log"
            heartbeat.parent.mkdir(parents=True, exist_ok=True)
            heartbeat.write_text("Attack loop active.\n", encoding="utf-8")
        sleep(1.5)
    print("[SIM] Continuous attack loop stopped")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Safe CRDS ransomware activity simulator")
    parser.add_argument(
        "--with-note",
        action="store_true",
        help="Create README.txt ransom-note simulation for Generic classification",
    )
    parser.add_argument(
        "--loop",
        action="store_true",
        help="Run continuously until process is terminated",
    )
    args = parser.parse_args()
    if args.loop:
        run_attack_loop(lambda: True, with_note=args.with_note)
    else:
        simulate_once(with_note=args.with_note)
