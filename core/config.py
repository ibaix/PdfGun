import json
import os
from pathlib import Path

CONFIG_DIR = Path(os.environ.get("APPDATA", "")) / "BatchPdfPrinter"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "last_printer": "",
    "sumatra_path": "",
}


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return DEFAULT_CONFIG.copy()
    try:
        with CONFIG_FILE.open(encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return DEFAULT_CONFIG.copy()
    return {**DEFAULT_CONFIG, **data}


def save_config(config: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with CONFIG_FILE.open("w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
