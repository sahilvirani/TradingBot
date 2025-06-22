from __future__ import annotations

from pathlib import Path
from typing import Any, List

import yaml

_cfg_path = Path("config/tradingbot.yaml")
_default_cfg_path = Path(__file__).parent / "default.yaml"


def _load_config() -> dict[str, Any]:
    """Load config from tradingbot.yaml or fall back to default.yaml."""
    if _cfg_path.exists():
        cfg_path = _cfg_path
    elif _default_cfg_path.exists():
        cfg_path = _default_cfg_path
    else:
        raise FileNotFoundError(
            "Could not find config/tradingbot.yaml or default config"
        )

    with cfg_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


_cfg_dict = _load_config()

strategies: List[dict[str, Any]] = _cfg_dict.get(
    "strategies", []
)  # type: ignore[assignment]
backtest = _cfg_dict.get("backtest", {})  # exported for convenience

__all__: list[str] = ["strategies", "backtest"]
