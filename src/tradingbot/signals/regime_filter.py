# File: src/tradingbot/signals/regime_filter.py
import pandas as pd

from tradingbot.features.vol_regime import compute_regime, load_spy_vol, load_vix


def apply_regime_filter(
    signal: pd.Series, allowed: tuple[str, ...] = ("calm", "normal")
) -> pd.Series:
    """Filter signals to only trade in allowed market regimes."""

    # Handle empty signals
    if signal.empty:
        return signal.copy()

    # If all regimes are allowed, skip regime filtering
    if "turbulent" in allowed and "calm" in allowed and "normal" in allowed:
        return signal.copy()

    try:
        # Determine start date from signal index
        start_date = str(signal.index.min())[:10]  # Get YYYY-MM-DD format

        # Load market data
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
