# File: src/tradingbot/backtest/is_oos_eval.py
from __future__ import annotations

from pathlib import Path

import pandas as pd

from tradingbot.backtest.metrics import backtest_metrics
from tradingbot.backtest.save_params import load_saved_params
from tradingbot.data.sp500_top50 import get_top50_symbols
from tradingbot.data.yfinance_downloader import download_stock_data
from tradingbot.signals.mean_reversion import generate_mr_signal
from tradingbot.signals.momentum import generate_mom_signal
from tradingbot.signals.regime_filter import apply_regime_filter

RESULTS_PATH = Path("data/is_oos_results.csv")


def run_is_oos_test(
    symbols: list[str] | None = None,
    is_start: str = "2023-01-01",
    is_end: str = "2025-01-01",
    oos_start: str = "2025-01-02",
    oos_end: str = "2025-05-01",
):
    symbols = symbols or get_top50_symbols()
    cfgs = load_saved_params()  # from Sprint 10
    rows = []

    for sym in symbols:
        df = download_stock_data(sym, start=is_start)
        df_is = df.loc[is_start:is_end]
        df_oos = df.loc[oos_start:oos_end]

        for cfg in cfgs:
            sig_mr = generate_mr_signal(
                df_is, enter_thresh=cfg["enter_thresh"], window=cfg["window"]
            )
            sig_mom = generate_mom_signal(
                df_is,
                long_thresh=cfg["long_thresh"],
                short_thresh=cfg["short_thresh"],
                window=cfg["window"],
            )
            combined_is = ((sig_mr + sig_mom) / 2).round().clip(-1, 1)
            combined_is = apply_regime_filter(combined_is)

            # APPLY SAME PARAMS ON OOS WITHOUT REFITTING
            sig_mr_oos = generate_mr_signal(
                df_oos, enter_thresh=cfg["enter_thresh"], window=cfg["window"]
            )
            sig_mom_oos = generate_mom_signal(
                df_oos,
                long_thresh=cfg["long_thresh"],
                short_thresh=cfg["short_thresh"],
                window=cfg["window"],
            )
            combined_oos = ((sig_mr_oos + sig_mom_oos) / 2).round().clip(-1, 1)
            combined_oos = apply_regime_filter(combined_oos)

            is_stats = backtest_metrics(df_is["Close"], combined_is, df_full=df_is)
            oos_stats = backtest_metrics(df_oos["Close"], combined_oos, df_full=df_oos)

            rows.append(
                {
                    "Symbol": sym,
                    **{f"IS_{k}": v for k, v in is_stats.items()},
                    **{f"OOS_{k}": v for k, v in oos_stats.items()},
                    **cfg,
                }
            )

    res = pd.DataFrame(rows)
    RESULTS_PATH.parent.mkdir(exist_ok=True)
    res.to_csv(RESULTS_PATH, index=False)
    return res
