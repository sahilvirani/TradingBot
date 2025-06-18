# File: src/tradingbot/backtest/metrics.py

import pandas as pd

from tradingbot.backtest.vbt_runner import run_backtest


def backtest_metrics(price: pd.Series, signal: pd.Series) -> dict[str, float]:
    pf = run_backtest(price, signal)
    return {
        "Return[%]": pf.total_return() * 100,
        "Sharpe": pf.sharpe_ratio(),  # type: ignore
        "MaxDD[%]": pf.max_drawdown() * 100,  # type: ignore
        "Trades": pf.trades.count(),
    }
