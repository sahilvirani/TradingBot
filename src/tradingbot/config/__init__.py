from __future__ import annotations

from pathlib import Path
from typing import Any, List

import yaml

_cfg_path = Path("config/tradingbot.yaml")

if not _cfg_path.exists():
    raise FileNotFoundError("Could not find config/tradingbot.yaml")

with _cfg_path.open("r", encoding="utf-8") as f:
    _cfg_dict: dict[str, Any] = yaml.safe_load(f) or {}

strategies: List[dict[str, Any]] = _cfg_dict.get(
    "strategies", []
)  # type: ignore[assignment]
backtest = _cfg_dict.get("backtest", {})  # exported for convenience

__all__: list[str] = ["strategies", "backtest"]
