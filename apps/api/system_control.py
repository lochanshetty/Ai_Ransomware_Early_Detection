from __future__ import annotations

from pathlib import Path

from apps.deception.models import HoneypotFile
from apps.detection.models import Alert, Threat
from apps.monitoring.services import monitor_runtime
from utils.encryption import decrypt_file


def stop_attack_and_reset_state() -> dict:
    """
    Shared stop/reset flow used by dashboard and honeypot refresh endpoints.
    """

    monitor_runtime.stop_attack()

    base_dir = Path(__file__).resolve().parents[2]
    demo_dir = base_dir / "demo_files"
    restored_files = 0
    for locked_file in demo_dir.glob("*.locked"):
        original = locked_file.with_name(locked_file.name.replace(".locked", ""))
        if original.exists():
            continue
        decrypt_file(str(locked_file))
        restored_files += 1

    reset_count = HoneypotFile.objects.filter(is_triggered=True).update(is_triggered=False)
    resolved_alerts = Alert.objects.filter(status="open").update(status="resolved")
    honeypot_threats_qs = Threat.objects.filter(
        analysis_payload__honeypot_triggered=True,
    )
    cleared_honeypot_threats = honeypot_threats_qs.count()
    honeypot_threats_qs.delete()

    return {
        "status": "stopped",
        "restored_files": restored_files,
        "honeypots_reset": reset_count,
        "alerts_resolved": resolved_alerts,
        "cleared_honeypot_threats": cleared_honeypot_threats,
        **monitor_runtime.system_state(),
    }
