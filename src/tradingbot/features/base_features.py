from typing import cast

import pandas as pd


def compute_daily_returns(df: pd.DataFrame) -> pd.Series:
    """
    Compute daily percentage returns from Close prices.

    Args:
        df: DataFrame with 'Close' column

    Returns:
        Series with daily percentage returns
    """
    # Pandas returns Series here but the type stubs expose
    # `Series | DataFrame | Unknown`.  Cast to silence the checker.
    return cast(pd.Series, df["Close"].pct_change().fillna(0))


def compute_rolling_zscore(series: pd.Series, window: int = 20) -> pd.Series:
    """
    Compute rolling z-score for a given series.

    Args:
        series: Input series (e.g., Close prices)
        window: Rolling window size for mean and std calculation

    Returns:
        Series with rolling z-scores
    """
    rolling_mean = series.rolling(window=window).mean()
    rolling_std = series.rolling(window=window).std()

    # Avoid division by zero
    zscore = (series - rolling_mean) / rolling_std
    # rolling_std can be zero initially; resulting NaNs are expected.
    return cast(pd.Series, zscore)
