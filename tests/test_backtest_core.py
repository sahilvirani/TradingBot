# File: tests/test_backtest_core.py

from typing import cast

import pandas as pd

from tradingbot.backtest.metrics import backtest_metrics
from tradingbot.data.yfinance_downloader import download_stock_data
from tradingbot.signals.mean_reversion import generate_mr_signal


def test_backtest_runner():
    df = download_stock_data("AAPL", start="2023-01-01", end="2024-01-01")
    sig = generate_mr_signal(df)

    stats = backtest_metrics(df["Close"], sig)

    # Check that we get reasonable output
    assert stats["CAGR"] is not None
    assert stats["Sharpe"] is not None
    assert stats["Max_DD"] <= 0  # max drawdown should be negative
