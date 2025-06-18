# File: src/tradingbot/backtest/aggregate.py

import pandas as pd


def aggregate_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Group by parameter sets and compute mean Sharpe & Return across tickers.
    """
    group_cols = ["enter_thresh", "window", "long_thresh", "short_thresh"]
    agg = df.groupby(group_cols).agg(
        {"Sharpe": "mean", "Return[%]": "mean", "MaxDD[%]": "mean"}
    )
    return agg.sort_values(by="Sharpe", ascending=False)  # type: ignore
