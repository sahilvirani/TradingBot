# File: src/tradingbot/evaluation/risk_grid.py
import itertools

import pandas as pd

from tradingbot.config import strategies
from tradingbot.data.sp500_top50 import get_top50_symbols
from tradingbot.evaluation.benchmark_compare import benchmark_comparison

UNIVERSE = get_top50_symbols()

GRID = {
    "risk_pct": [0.0004, 0.0005, 0.0006, 0.0007],
    "stop_mult": [1.5, 2.0, 2.5],
}


def run():
    rows = []
    for strat in strategies:
        if not strat.get("name"):  # safety
            continue
        for rp, sm in itertools.product(GRID["risk_pct"], GRID["stop_mult"]):
            m = benchmark_comparison(
                strat,
                UNIVERSE,
                risk_pct=rp,
                stop_mult=sm,
                use_atr_overlay=True,
                return_dict=True,
            )
            m.update({"strategy": strat["name"], "risk_pct": rp, "stop_mult": sm})
            rows.append(m)
    df = pd.DataFrame(rows)
    df.to_csv("reports/risk_grid_results.csv", index=False)
    print(
        df.groupby("strategy")[["sharpe", "max_dd"]].describe(
            percentiles=[0.1, 0.5, 0.9]
        )
    )


if __name__ == "__main__":
    run()
