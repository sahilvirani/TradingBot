# File: src/tradingbot/backtest/metrics.py

import pandas as pd

from tradingbot.backtest.vbt_runner import run_backtest


def backtest_metrics(
    price: pd.Series, signal: pd.Series, df_full: pd.DataFrame | None = None
) -> dict[str, float]:
    pf = run_backtest(price, signal, df_full=df_full)

    # Extract scalar values from potentially Series results
    total_return = pf.total_return()
    if isinstance(total_return, pd.Series):
        total_return = total_return.iloc[0]

    sharpe = pf.sharpe_ratio()  # type: ignore
    if isinstance(sharpe, pd.Series):
        sharpe = sharpe.iloc[0]

    max_dd = pf.max_drawdown()  # type: ignore
    if isinstance(max_dd, pd.Series):
        max_dd = max_dd.iloc[0]

    trades = pf.trades.count()
    if isinstance(trades, pd.Series):
        trades = trades.iloc[0]

    return {
        "Return[%]": float(total_return * 100),
        "Sharpe": float(sharpe),
        "MaxDD[%]": float(max_dd * 100),
        "Trades": int(trades),
    }
