# File: src/tradingbot/risk/atr.py

import pandas as pd

__all__ = [
    "calc_atr",
    "position_size",
]


def calc_atr(df: pd.DataFrame, window: int = 14) -> pd.Series:
    """Calculate the Average True Range (ATR).

    Parameters
    ----------
    df : pd.DataFrame
        Must contain columns "High", "Low", and "Close".
    window : int, default 14
        Rolling window length.
    """
    high = df["High"]
    low = df["Low"]
    close = df["Close"]

    prev_close = close.shift()

    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()

    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window).mean().bfill()
    return atr


def position_size(equity: float, atr: float, risk_pct: float = 0.003) -> int:
    """Return share quantity so that a 2×ATR adverse move risks *risk_pct* of equity.

    Returns 0 if ATR is zero or negative.
    """
    if atr <= 0 or equity <= 0:
        return 0

    dollar_risk = equity * risk_pct
    qty_float = dollar_risk / (2.0 * atr)
    return max(int(qty_float), 0)
