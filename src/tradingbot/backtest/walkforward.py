# File: src/tradingbot/backtest/walkforward.py

from __future__ import annotations

from itertools import product

import pandas as pd

from tradingbot.backtest.metrics import backtest_metrics
from tradingbot.signals.mean_reversion import generate_mr_signal


def walk_forward_optimize(
    df: pd.DataFrame,
    param_grid: dict[str, list],
    is_days: int = 504,  # 2 yrs
    oos_days: int = 63,  # 3 mo
) -> pd.DataFrame:
    """
    Grid-search MR parameters on rolling IS window, test on next OOS window.
    Returns a DataFrame with OOS performance per fold.
    """
    results = []
    idx_start = 0
    while idx_start + is_days + oos_days <= len(df):
        is_slice = df.iloc[idx_start : idx_start + is_days]
        oos_slice = df.iloc[idx_start + is_days : idx_start + is_days + oos_days]

        best_param, best_sharpe = None, -9e9
        for params in product(*param_grid.values()):
            kwargs = dict(zip(param_grid.keys(), params))
            sig_is = generate_mr_signal(is_slice, **kwargs)
            m = backtest_metrics(is_slice["Close"], sig_is)
            if m["Sharpe"] > best_sharpe:
                best_param, best_sharpe = kwargs, m["Sharpe"]

        # evaluate on OOS
        if best_param is not None:
            sig_oos = generate_mr_signal(oos_slice, **best_param)
            m = backtest_metrics(oos_slice["Close"], sig_oos)
            m.update(best_param)
            m["FoldStart"] = oos_slice.index[0]
            results.append(m)

        idx_start += oos_days  # slide

    return pd.DataFrame(results)
