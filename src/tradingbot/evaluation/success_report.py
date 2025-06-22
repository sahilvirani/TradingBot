from __future__ import annotations

from pathlib import Path

import pandas as pd
from tabulate import tabulate

from tradingbot.config import strategies
from tradingbot.evaluation.benchmark_compare import benchmark_comparison

# Fallback universe helper
try:
    from tradingbot.data.sp500_top50 import get_top50_symbols  # type: ignore

    UNIVERSE = get_top50_symbols()
except ImportError:
    from tradingbot.data.universe import get_universe

    # If top-50 helper missing, fall back to cached CSV list or default 5-stock list.
    UNIVERSE = get_universe()

OUT_PATH = Path("reports/success_report.csv")
TARGETS = {"sharpe": 0.70, "max_dd": -0.15, "excess_periods": 2}


def evaluate_all() -> pd.DataFrame:
    rows: list[dict] = []
    for cfg in strategies:
        name = cfg.get("name", "<unnamed>")
        print(f"Running {name} …")
        metrics = benchmark_comparison(
            cfg,
            UNIVERSE,
            risk_pct=0.0006,  # 0.06% of equity per trade (final ultra-low risk)
            use_atr_overlay=True,  # Use ATR overlay for position sizing
            return_dict=True,  # Return metrics dictionary
        )
        if metrics is None:
            # fallback in case function returns None
            continue
        row = {"name": name, **metrics}
        row["meets_all"] = (
            metrics["sharpe"] >= TARGETS["sharpe"]
            and metrics["max_dd"] >= TARGETS["max_dd"]
            and metrics["excess_periods"] >= TARGETS["excess_periods"]
        )
        rows.append(row)

    df = pd.DataFrame(rows)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_PATH, index=False)
    return df


def print_summary(df: pd.DataFrame):
    active = int((df["trades"] > 0).sum())
    total = len(df)
    print(f"\nActive configs: {active}/{total}  ({active/total*100:.1f}%)")
    winners = df[df["meets_all"]]
    print(f"Configs meeting ALL targets: {len(winners)}")
    cols = ["name", "sharpe", "max_dd", "excess_periods", "trades", "meets_all"]
    print(tabulate(df[cols], headers="keys", floatfmt=".2f"))


if __name__ == "__main__":
    _df = evaluate_all()
    print_summary(_df)
