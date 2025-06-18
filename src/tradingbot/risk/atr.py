# File: src/tradingbot/risk/atr.py

from typing import cast

import pandas as pd
from ta.volatility import AverageTrueRange


def compute_atr(df: pd.DataFrame, window: int = 14) -> pd.Series:
    """Average True Range in $."""
    return AverageTrueRange(
        high=cast(pd.Series, df["High"]),
        low=cast(pd.Series, df["Low"]),
        close=cast(pd.Series, df["Close"]),
        window=window,
    ).average_true_range()
