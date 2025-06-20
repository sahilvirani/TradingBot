# File: src/tradingbot/signals/regime_filter.py
import pandas as pd

from tradingbot.features.vol_regime import compute_regime, load_spy_vol, load_vix


def apply_regime_filter(
    signal: pd.Series, allowed: tuple[str, ...] = ("calm", "normal")
) -> pd.Series:
    """Zero-out signal on dates whose regime not in `allowed`."""
    start_date = str(signal.index.min())[:10]  # Get YYYY-MM-DD format
    vix = load_vix(start=start_date)
    vol = load_spy_vol(start=start_date)
    regime = compute_regime(vix, vol)
    aligned = regime.reindex(signal.index).ffill()
    return signal.where(aligned.isin(allowed), other=0)
