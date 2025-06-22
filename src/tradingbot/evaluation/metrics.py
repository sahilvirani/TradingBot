import numpy as np
import pandas as pd

__all__ = [
    "calc_sharpe",
    "calc_max_drawdown",
    "calc_cagr",
]


def calc_sharpe(daily_returns: pd.Series, risk_free_rate: float = 0.0) -> float:
    """Calculate annualised Sharpe ratio given daily returns.

    Parameters
    ----------
    daily_returns : pd.Series
        Series of daily returns expressed as fractional change (0.01 = 1 %).
    risk_free_rate : float, default 0.0
        Daily risk-free rate (already in daily terms, *not annual*).
    """
    # Ensure we have a proper Series
    if not isinstance(daily_returns, pd.Series):
        return 0.0

    excess_ret = daily_returns - risk_free_rate

    # Check if all returns are identical (constant)
    try:
        unique_count = excess_ret.nunique()
        if unique_count == 1:
            return 0.0
    except (TypeError, ValueError):
        # Fallback: check if std is effectively zero
        pass

    # Population std (ddof=0) to match most finance libraries when annualising
    std = excess_ret.std(ddof=0)

    # Handle case where std might be a Series or scalar
    if hasattr(std, "iloc"):
        std = float(std.iloc[0]) if len(std) > 0 else 0.0
    else:
        std = float(std) if not pd.isna(std) else 0.0

    if std == 0:
        return 0.0

    mean_ret = excess_ret.mean()
    if hasattr(mean_ret, "iloc"):
        mean_ret = float(mean_ret.iloc[0]) if len(mean_ret) > 0 else 0.0
    else:
        mean_ret = float(mean_ret) if not pd.isna(mean_ret) else 0.0

    sharpe = (mean_ret / std) * np.sqrt(252)
    return float(sharpe)


def calc_max_drawdown(equity_curve: pd.Series) -> float:
    """Return the maximum drawdown experienced by *equity_curve*.

    Parameters
    ----------
    equity_curve : pd.Series
        Series of cumulative equity values (e.g. portfolio value) indexed by date.

    Returns
    -------
    float
        Maximum drawdown as a negative fraction (e.g. -0.15 for −15 %).
    """
    cumulative_max = equity_curve.cummax()
    drawdown = equity_curve / cumulative_max - 1.0
    return float(drawdown.min())


def calc_cagr(equity_curve: pd.Series) -> float:
    """Compound Annual Growth Rate for the period spanned by *equity_curve*.

    Parameters
    ----------
    equity_curve : pd.Series
        Series of cumulative equity values indexed by date.

    Returns
    -------
    float
        CAGR as a decimal (0.12 = 12 %). Returns 0.0 if period < 1 day.
    """
    if equity_curve.empty:
        return 0.0

    start_value = float(equity_curve.iloc[0])
    end_value = float(equity_curve.iloc[-1])
    if start_value <= 0:
        return 0.0

    # Handle negative end values (total loss scenarios)
    if end_value <= 0:
        return -1.0  # Return -100% CAGR for total loss

    # Ensure we have datetime index
    if not isinstance(equity_curve.index, pd.DatetimeIndex):
        return 0.0

    # Calculate time difference in years
    start_date = equity_curve.index[0]
    end_date = equity_curve.index[-1]
    days = (end_date - start_date).days
    if days <= 0:
        return 0.0

    years = days / 365.25
    return float(((end_value / start_value) ** (1 / years)) - 1.0)
