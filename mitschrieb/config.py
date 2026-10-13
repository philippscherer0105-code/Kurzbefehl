"""API-Schlüssel aus Umgebungsvariable oder lokal gespeicherter Datei."""

from __future__ import annotations

import os
from pathlib import Path

DATA_DIR = Path(os.environ.get("MITSCHRIEB_DATA", Path(__file__).resolve().parent.parent / "data"))
KEY_FILE = DATA_DIR / "api_key.txt"


def api_key() -> str | None:
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if key:
        return key
    if KEY_FILE.exists():
        return KEY_FILE.read_text(encoding="utf-8").strip() or None
    return None


def save_api_key(key: str) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    KEY_FILE.write_text(key.strip(), encoding="utf-8")
    try:
        KEY_FILE.chmod(0o600)
    except OSError:
        pass
