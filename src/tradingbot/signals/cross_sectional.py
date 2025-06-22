from typing import Dict

import pandas as pd

__all__ = [
    "rank_top_n_df",
    "compute_return_matrix",
]


def rank_top_n_df(
    metric_df: pd.DataFrame, n: int, highest: bool = True
) -> pd.DataFrame:
    """Return DataFrame of 1/0 selecting top *n* per date.

    Parameters
    ----------
    metric_df : pd.DataFrame
        Index = datetime, columns = tickers; the values are the metric to rank.
        Higher values are better when *highest* is True.
    n : int
        Number of assets to select per row.
    highest : bool, default True
        If True, pick highest metric values. If False, pick lowest.
    """
    if n <= 0:
        raise ValueError("n must be positive")

    # dense ranking: 1 = best (highest or lowest)
    ranks = metric_df.rank(axis=1, ascending=not highest, method="dense")
    selection = (ranks <= n).astype(int)
    return selection


def universe_momentum_ok(metric_df: pd.DataFrame) -> pd.Series:
    """
    Returns a boolean Series (index = dates):
    True when average momentum across universe > 0.
    """
    return metric_df.mean(axis=1) > 0


def compute_return_matrix(
    price_data: Dict[str, pd.DataFrame], window: int = 60
) -> pd.DataFrame:
    """Compute trailing return matrix for each ticker over *window* days."""
    returns = {}
    for ticker, df in price_data.items():
        if "Close" not in df.columns:
            raise KeyError(f"Data for {ticker} missing 'Close' column")
        close = df["Close"]
        returns[ticker] = close.pct_change(window)
    return pd.DataFrame(returns).fillna(0.0)
