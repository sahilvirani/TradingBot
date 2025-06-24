from functools import lru_cache
import pandas as pd
from tradingbot.data.market_benchmarks import get_vix_series

@lru_cache(maxsize=1)
def cached_vix_series():
    v = get_vix_series()        # cached parquet, never re-downloads
    v.index = pd.to_datetime(v.index)
    return v

def throttle_risk_pct(base_risk: float, date, vix_series=None) -> float:
    """
    Throttle risk based on VIX level at given date.
    
    Parameters
    ----------
    base_risk : float
        Base risk percentage
    date : pd.Timestamp or str
        Date to check VIX level for
    vix_series : pd.Series, optional
        Pre-loaded VIX series. If None, will load from cache.
        
    Returns
    -------
    float
        Adjusted risk percentage
    """
    try:
        if vix_series is None:
            vix_data = cached_vix_series()  # Use the cached singleton
        else:
            vix_data = vix_series  # Use provided series
            
        if isinstance(date, str):
            date = pd.to_datetime(date)
        
        # Get VIX value for the date (use nearest available)
        vix_val = vix_data.asof(date)
        
        if pd.isna(vix_val):
            return base_risk
            
        # Simple throttling: reduce risk when VIX > 30
        if vix_val > 30:
            return base_risk * 0.5  # Half risk during high volatility
        elif vix_val > 20:
            return base_risk * 0.75  # Reduce risk moderately
        else:
            return base_risk  # Normal risk
            
    except Exception:
        # Fallback to base risk if VIX data unavailable
        return base_risk
