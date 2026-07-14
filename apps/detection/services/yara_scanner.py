"""Optional YARA rule scanning for file-based threat detection."""

from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_yara_module = None
_compiled_rules = None


def _load_yara():
    global _yara_module
    if _yara_module is not None:
        return _yara_module
    try:
        import yara  # type: ignore[import-untyped]
        _yara_module = yara
    except ImportError:
        _yara_module = False
    return _yara_module


def _rules_dir() -> Path:
    try:
        from django.conf import settings
        return Path(settings.BASE_DIR) / "rules" / "yara"
    except Exception:  # noqa: BLE001
        return Path(__file__).resolve().parents[2] / "rules" / "yara"


def _compile_rules():
    global _compiled_rules
    if _compiled_rules is not None:
        return _compiled_rules

    yara = _load_yara()
    if not yara:
        _compiled_rules = False
        return _compiled_rules

    rules_path = _rules_dir()
    rule_files = list(rules_path.glob("*.yar")) + list(rules_path.glob("*.yara"))
    if not rule_files:
        _compiled_rules = False
        return _compiled_rules

    try:
        filepaths = {f"rule_{idx}": str(path) for idx, path in enumerate(rule_files)}
        _compiled_rules = yara.compile(filepaths=filepaths)
    except Exception as exc:  # noqa: BLE001
        logger.warning("YARA compile failed: %s", exc)
        _compiled_rules = False
    return _compiled_rules


def scan_file(file_path: str) -> tuple[bool, list[str]]:
    """
    Scan a file with YARA rules if available.
    Returns (matched, rule_names).
    """

    rules = _compile_rules()
    if not rules:
        return False, []

    path = Path(file_path)
    if not path.is_file():
        return False, []

    try:
        matches = rules.match(str(path), timeout=5)
        names = [match.rule for match in matches]
        return bool(names), names
    except Exception as exc:  # noqa: BLE001
        logger.debug("YARA scan failed for %s: %s", file_path, exc)
        return False, []
