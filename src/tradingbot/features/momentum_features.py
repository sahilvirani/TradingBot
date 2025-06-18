# File: src/tradingbot/features/momentum_features.py

import numpy as np
import pandas as pd

from tradingbot.features.base_features import compute_daily_returns


def compute_cumulative_return(df: pd.DataFrame, window: int = 21) -> pd.Series:
    """Rolling cumulative return over `window` days."""
    returns = compute_daily_returns(df)
    return (1 + returns).rolling(window).apply(np.prod, raw=True) - 1


def compute_vol_adj_momentum(df: pd.DataFrame, window: int = 21) -> pd.Series:
    """
    Volatility-adjusted momentum (Sharpe proxy):
        cumulative_return / rolling_std(returns)
    """
    returns = compute_daily_returns(df)
    cum_ret = compute_cumulative_return(df, window)
    vol = returns.rolling(window).std()
    return cum_ret / vol.replace(0, np.nan)
