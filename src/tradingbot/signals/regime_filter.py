# File: src/tradingbot/signals/regime_filter.py
import pandas as pd

from tradingbot.features.vol_regime import (
    compute_regime, 
    load_spy_vol, 
    load_vix,
    load_spy_vol_cached,
    load_vix_cached
)


def apply_regime_filter(
    signal: pd.Series, 
    allowed: tuple[str, ...] = ("calm", "normal"),
    vix_series: pd.Series = None,
    spy_series: pd.Series = None,
) -> pd.Series:
    """Filter signals to only trade in allowed market regimes.
    
    Parameters
    ----------
    signal : pd.Series
        Trading signal to filter
    allowed : tuple[str, ...]
        Allowed regimes ('calm', 'normal', 'turbulent')
    vix_series : pd.Series, optional
        Pre-loaded VIX series to avoid downloads
    spy_series : pd.Series, optional
        Pre-loaded SPY series to avoid downloads
    """

    # Handle empty signals
    if signal.empty:
        return signal.copy()

    # If all regimes are allowed, skip regime filtering
    if "turbulent" in allowed and "calm" in allowed and "normal" in allowed:
        return signal.copy()

    try:
        # Determine start date from signal index
        start_date = str(signal.index.min())[:10]  # Get YYYY-MM-DD format

        # Load market data - use cached versions if available
        if vix_series is not None and spy_series is not None:
            vix = load_vix_cached(vix_series, start=start_date)
            spy_vol = load_spy_vol_cached(spy_series, start=start_date)
        else:
            # Fallback to downloading
            vix = load_vix(start=start_date)
            spy_vol = load_spy_vol(start=start_date)

        # Compute regime
        regime = compute_regime(vix, spy_vol)

        # Align regime with signal dates and fill forward
        aligned = regime.reindex(signal.index).ffill()

        # Filter: zero out signals not in allowed regimes
        mask = aligned.isin(allowed)
        return signal.where(mask, 0)
    except Exception:
        # If regime filtering fails, return original signal
        return signal.copy()
