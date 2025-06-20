# File: src/tradingbot/features/vol_regime.py
import pandas as pd
import yfinance as yf


def load_vix(start: str = "2015-01-01") -> pd.Series:
    """Fetch daily VIX close."""
    data = yf.download("^VIX", start=start)
    if data is None or data.empty:
        raise ValueError("Failed to download VIX data")

    # Handle multi-level columns from yfinance
    if isinstance(data.columns, pd.MultiIndex):
        vix = data[("Close", "^VIX")]
    else:
        vix = data["Close"]

    # Ensure it's a Series and set name
    vix = pd.Series(vix, index=vix.index, name="VIX")
    return vix


def load_spy_vol(start: str = "2015-01-01", window: int = 21) -> pd.Series:
    """Rolling stdev of SPY returns, annualised."""
    data = yf.download("SPY", start=start)
    if data is None or data.empty:
        raise ValueError("Failed to download SPY data")

    # Handle multi-level columns from yfinance
    if isinstance(data.columns, pd.MultiIndex):
        spy = data[("Close", "SPY")]
    else:
        spy = data["Close"]

    # Ensure it's a Series
    spy = pd.Series(spy, index=spy.index)
    ret = spy.pct_change()
    vol = ret.rolling(window).std() * (252**0.5)
    vol.name = "SPY_vol"
    return vol


def compute_regime(vix: pd.Series, spy_vol: pd.Series) -> pd.Series:
    """
    Regime:
      calm        – VIX < 33rd pct & SPY_vol < 33rd pct
      turbulent   – VIX > 66th pct | SPY_vol > 66th pct
      normal      – otherwise
    """
    joined = pd.concat([vix, spy_vol], axis=1).dropna()
    vix_pctl = joined["VIX"].rank(pct=True)
    vol_pctl = joined["SPY_vol"].rank(pct=True)

    regime = pd.Series("normal", index=joined.index)
    regime[(vix_pctl < 0.33) & (vol_pctl < 0.33)] = "calm"
    regime[(vix_pctl > 0.66) | (vol_pctl > 0.66)] = "turbulent"
    return regime
