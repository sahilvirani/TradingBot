from functools import lru_cache
from pathlib import Path

import pandas as pd
import yfinance as yf

_CACHE = Path("data/vix_close.parquet")


def _download_and_cache() -> pd.Series:
    """Download VIX data and cache it locally."""
    try:
        vix_data = yf.download("^VIX", start="2010-01-01", progress=False)
        if vix_data is None or vix_data.empty:
            return pd.Series(dtype=float)
        vix = vix_data["Close"]
        _CACHE.parent.mkdir(exist_ok=True)
        vix.to_frame("Close").to_parquet(_CACHE)
        return vix
    except Exception:
        # Return empty series if download fails
        return pd.Series(dtype=float)


@lru_cache(maxsize=1)
def vix_series() -> pd.Series:
    """Get VIX series from cache or download if needed."""
    if _CACHE.exists():
        try:
            return pd.read_parquet(_CACHE)["Close"]
        except Exception:
            pass
    return _download_and_cache()


def throttle_risk_pct(base_risk: float, date: pd.Timestamp, thr: float = 25.0) -> float:
    """Return reduced risk when VIX > threshold."""
    try:
        vix = vix_series()
        if date in vix.index and vix.loc[date] > thr:
            return base_risk * 0.5  # cut risk in half above threshold
        return base_risk
    except Exception:
        return base_risk
