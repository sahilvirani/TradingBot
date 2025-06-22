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
    excess_ret = daily_returns - risk_free_rate
    # Population std (ddof=0) to match most finance libraries when annualising
    std = excess_ret.std(ddof=0)
    if std == 0 or pd.isna(std):
        return 0.0
    sharpe = (excess_ret.mean() / std) * np.sqrt(252)
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

    # Ensure we have datetime index
    if not isinstance(equity_curve.index, pd.DatetimeIndex):
        return 0.0

    days = (equity_curve.index[-1] - equity_curve.index[0]).days
    if days <= 0:
        return 0.0

    years = days / 365.25
    return float((end_value / start_value) ** (1 / years) - 1.0)
