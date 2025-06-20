# File: src/tradingbot/signals/momentum.py

import pandas as pd

from tradingbot.features.momentum_features import (
    compute_cumulative_return,
    compute_vol_adj_momentum,
)


def generate_mom_signal(
    df: pd.DataFrame,
    window: int = 21,
    long_thresh: float = 0.01,
    short_thresh: float = -0.01,
    use_vol_adjust: bool = False,
) -> pd.Series:
    """
    Momentum signal:
      +1  if momentum > long_thresh
      -1  if momentum < short_thresh
       0  otherwise
    """
    mom = (
        compute_vol_adj_momentum(df, window)
        if use_vol_adjust
        else compute_cumulative_return(df, window)
    )

    signal = pd.Series(0, index=df.index)
    signal[mom > long_thresh] = 1
    signal[mom < short_thresh] = -1
    return signal
