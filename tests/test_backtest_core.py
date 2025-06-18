# File: tests/test_backtest_core.py

from typing import cast

import pandas as pd

from tradingbot.backtest.metrics import backtest_metrics
from tradingbot.data.yfinance_downloader import download_stock_data
from tradingbot.signals.mean_reversion import generate_mr_signal


def test_backtest_runner():
    df = download_stock_data("AAPL", start="2023-01-01")
    sig_mr = generate_mr_signal(df)

    close_series = cast(pd.Series, df["Close"])
    stats = backtest_metrics(close_series, sig_mr)

    # sanity checks
    assert stats["Trades"] > 0
    assert -100 < stats["Return[%]"] < 500  # guardrails, not strict
