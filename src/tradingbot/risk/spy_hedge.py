import pandas as pd
import yfinance as yf

from tradingbot.risk.vix_filter import vix_series

_SPY = yf.download("SPY", start="2010-01-01", progress=False)["Close"]


def hedge_weight(date: pd.Timestamp, thr: float = 25.0) -> float:
    """Return -1 if VIX>thr OR SPY below 200-DMA, else 0."""
    vix = vix_series()
    if date not in vix.index:
        return 0
    vix_hi = vix.loc[date] > thr
    spy_200 = _SPY.rolling(200).mean()
    trend_dn = _SPY.loc[date] < spy_200.loc[date]
    return -1.0 if (vix_hi or trend_dn) else 0.0
