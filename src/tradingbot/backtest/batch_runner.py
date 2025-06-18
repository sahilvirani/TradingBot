# File: src/tradingbot/backtest/batch_runner.py

from __future__ import annotations

from itertools import product
from typing import Any, cast

import pandas as pd

from tradingbot.backtest.metrics import backtest_metrics
from tradingbot.data.universe import get_universe
from tradingbot.data.yfinance_downloader import download_stock_data
from tradingbot.signals.mean_reversion import generate_mr_signal
from tradingbot.signals.momentum import generate_mom_signal


def grid_search_batch(
    start: str = "2022-01-03",
    end: str | None = None,
    universe: list[str] | None = None,
) -> pd.DataFrame:
    """
    Runs parameter grid across multiple tickers and returns aggregated metrics.
    """
    universe = get_universe(universe)
    rows = []
    mr_grid = dict(enter_thresh=[-0.5, -1.0], window=[20, 40])
    mom_grid = dict(long_thresh=[0.05], short_thresh=[-0.05], window=[21])

    for symbol in universe:
        df = download_stock_data(symbol, start=start)
        if end:
            df = df.loc[:end]

        for mr_params in product(*mr_grid.values()):
            enter_thresh, window_mr = mr_params
            sig_mr = generate_mr_signal(
                df, enter_thresh=enter_thresh, window=int(window_mr)
            )

            for mom_params in product(*mom_grid.values()):
                long_thresh, short_thresh, window_mom = mom_params
                sig_mom = generate_mom_signal(
                    df,
                    long_thresh=long_thresh,
                    short_thresh=short_thresh,
                    window=int(window_mom),
                )

                # simple ensemble: average signals and round
                combined = ((sig_mr + sig_mom) / 2).round().clip(-1, 1)

                close_series = cast(pd.Series, df["Close"])
                m = backtest_metrics(close_series, combined)

                # Create result with proper types
                result: dict[str, Any] = dict(m)
                result.update(
                    {
                        "enter_thresh": enter_thresh,
                        "window": int(window_mr),
                        "long_thresh": long_thresh,
                        "short_thresh": short_thresh,
                        "Symbol": symbol,
                    }
                )
                rows.append(result)

    return pd.DataFrame(rows)
