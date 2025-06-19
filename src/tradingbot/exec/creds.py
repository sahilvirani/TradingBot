# File: src/tradingbot/exec/creds.py
from pathlib import Path

import yaml


def load_creds(path: str | Path = "config/credentials.yaml") -> dict:
    """Load API keys; raise if file missing."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            "No credentials.yaml – copy config/credentials_example.yaml "
            "and fill your keys."
        )
    return yaml.safe_load(path.read_text())
