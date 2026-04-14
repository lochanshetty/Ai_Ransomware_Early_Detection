"""
One-command CRDS demo runner.

Usage:
1) Start Django server in another terminal:
   python manage.py runserver
2) Run this script:
   python run_demo.py
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

from utils.encryption import decrypt_file

BASE_URL = "http://127.0.0.1:8000"
ROOT = Path(__file__).resolve().parent


def _reset_demo_files():
    """Resets previously encrypted/renamed *.locked files for repeatable demos."""

    demo_dir = ROOT / "demo_files"
    for locked in demo_dir.glob("*.locked"):
        original = locked.with_name(locked.name.replace(".locked", ""))
        if original.exists():
            continue
        decrypt_file(str(locked))
        print(f"[DEMO] Reset file: {locked.name} -> {original.name}")


def _request_json(path: str, method: str = "GET", body: dict | None = None):
    payload = None
    headers = {}
    if body is not None:
        payload = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = Request(f"{BASE_URL}{path}", data=payload, headers=headers, method=method)
    with urlopen(request, timeout=8) as response:
        response_text = response.read().decode("utf-8")
    return json.loads(response_text)


def run_demo():
    print("[DEMO] Starting CRDS demo flow...")
    try:
        start = _request_json("/monitor/start", method="POST")
    except URLError:
        print("[DEMO] Could not reach Django server at http://127.0.0.1:8000")
        print("[DEMO] Start server first: python manage.py runserver")
        sys.exit(1)

    print(f"[DEMO] Monitor response: {start}")
    protected_sample = str((ROOT / "demo_files" / "accounts.csv").resolve())
    registry_response = _request_json(
        "/registry/add",
        method="POST",
        body={"file_path": protected_sample},
    )
    print(f"[DEMO] Registry response: {registry_response}")
    _reset_demo_files()
    print("[DEMO] Running safe ransomware simulation...")
    subprocess.run([sys.executable, str(ROOT / "simulate_attack.py")], check=True)

    logs = _request_json("/monitor/logs")
    threats = _request_json("/detect/threats")

    log_count = len(logs.get("results", []))
    threat_rows = threats.get("results", []) if isinstance(threats, dict) else threats
    threat_count = len(threat_rows) if isinstance(threat_rows, list) else 0

    print("[DEMO] Completed.")
    print(f"[DEMO] Latest logs captured: {log_count}")
    print(f"[DEMO] Threats detected: {threat_count}")
    if threat_count:
        top = threat_rows[0]
        print(
            "[DEMO] Latest threat -> "
            f"level={top.get('threat_level')} "
            f"score={top.get('confidence_score')} "
            f"reason={top.get('reason')}"
        )


if __name__ == "__main__":
    run_demo()
