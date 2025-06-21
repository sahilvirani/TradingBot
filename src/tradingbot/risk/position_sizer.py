# File: src/tradingbot/risk/position_sizer.py

import numpy as np
import pandas as pd

from tradingbot.risk.atr import calc_atr


def atr_position_size(
    df: pd.DataFrame,
    risk_per_trade: float = 0.01,  # risk 1 % of equity per trade
    kelly_frac: float = 0.25,  # cap leverage at 25 % Kelly
    init_equity: float = 1_000_000,
) -> pd.Series:
    """
    Shares = (risk_per_trade * equity) / (2 * ATR)   [2 ATR stop distance]
    Leverage is capped by Kelly fraction.
    """
    atr = calc_atr(df)
    dollar_risk = risk_per_trade * init_equity
    shares = dollar_risk / (2 * atr.replace(0, np.nan))
    max_shares = init_equity * kelly_frac / df["Close"]
    shares = np.minimum(shares, max_shares)
    return shares.fillna(0).round().astype(int)
