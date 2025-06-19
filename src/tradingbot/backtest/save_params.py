# File: src/tradingbot/backtest/save_params.py

from pathlib import Path

import pandas as pd
import yaml

CONFIG_PATH = Path("config/best_params.yaml")


def save_top_params(agg_df: pd.DataFrame, top_n: int = 5) -> None:
    """
    Save the top-N parameter rows (by Sharpe) to YAML.
    """
    best = (
        agg_df.sort_values("Sharpe", ascending=False)
        .head(top_n)
        .reset_index()
        .to_dict(orient="records")
    )
    CONFIG_PATH.parent.mkdir(exist_ok=True)
    with CONFIG_PATH.open("w") as f:
        yaml.safe_dump(best, f)


def load_saved_params() -> list[dict]:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError("Run save_top_params first.")
    return yaml.safe_load(CONFIG_PATH.read_text())
