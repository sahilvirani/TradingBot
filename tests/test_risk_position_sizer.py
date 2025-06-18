# File: tests/test_risk_position_sizer.py

from typing import cast

import pandas as pd

from tradingbot.backtest.metrics import backtest_metrics
from tradingbot.data.yfinance_downloader import download_stock_data
from tradingbot.signals.mean_reversion import generate_mr_signal


def test_atr_sizer_works():
    df = download_stock_data("AAPL", start="2023-01-01")
    sig = generate_mr_signal(df)

    close_series = cast(pd.Series, df["Close"])
    stats = backtest_metrics(close_series, sig)  # uses df without ATR sizing

    stats_atr = backtest_metrics(close_series, sig, df_full=df)  # ATR sizing via runner

    # Ensure trades exist and share counts differ
    assert stats["Trades"] > 0 and stats_atr["Trades"] > 0
    assert stats != stats_atr  # sizing should change metrics
