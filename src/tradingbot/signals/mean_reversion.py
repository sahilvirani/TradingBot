# File: src/tradingbot/signals/mean_reversion.py

from typing import cast

import pandas as pd

from tradingbot.features.base_features import compute_rolling_zscore


def generate_mr_signal(
    df: pd.DataFrame,
    enter_thresh: float = -1.0,
    exit_thresh: float = 0.0,
    window: int = 20,
) -> pd.Series:
    """
    Mean-reversion long-only signal:
    +1  when z-score < enter_thresh
     0  when z-score > exit_thresh
    Args:
        df           : DataFrame with 'Close'
        enter_thresh : enter when z-score below this
        exit_thresh  : flatten when z-score above this
        window       : rolling window for z-score
    Returns:
        pd.Series of {0,1} aligned with df.index
    """
    close_series = cast(pd.Series, df["Close"])
    z = compute_rolling_zscore(close_series, window)
    signal = (z < enter_thresh).astype(int)  # 1 = long
    signal[z > exit_thresh] = 0  # flat
    return signal


def generate_mr_long_short(
    df: pd.DataFrame,
    long_enter: float = -1.0,
    short_enter: float = 1.0,
    exit_thresh: float = 0.0,
    window: int = 20,
) -> pd.Series:
    """
    Symmetric long-short MR signal:
     +1 when z < long_enter
     -1 when z > short_enter
      0 when |z| < exit_thresh
    """
    close_series = cast(pd.Series, df["Close"])
    z = compute_rolling_zscore(close_series, window)
    signal = pd.Series(0, index=df.index)

    signal[z < long_enter] = 1
    signal[z > short_enter] = -1
    signal[z.abs() < exit_thresh] = 0
    return signal
