# File: tests/test_risk_position_sizer.py

from typing import cast

import pandas as pd

from tradingbot.backtest.metrics import backtest_metrics
from tradingbot.data.yfinance_downloader import download_stock_data
from tradingbot.signals.mean_reversion import generate_mr_signal
from tradingbot.risk.atr import calc_atr, position_size


def test_atr_sizer_works():
    df = download_stock_data("AAPL", start="2023-01-01", end="2024-01-01")
    atr = calc_atr(df, window=14)
    assert atr.notna().sum() > 0

    # position_size function should work
    pos = position_size(equity=100000, atr=2.5, risk_pct=0.01)
    assert pos > 0

    sig = generate_mr_signal(df)

    close_series = cast(pd.Series, df["Close"])
    stats = backtest_metrics(close_series, sig)  # uses df without ATR sizing

    stats_atr = backtest_metrics(close_series, sig, df_full=df)  # ATR sizing via runner

    # Ensure trades exist and share counts differ
    assert stats["Trades"] > 0 and stats_atr["Trades"] > 0
    assert stats != stats_atr  # sizing should change metrics

    # assert basic expectations
    assert len(sig) == len(df)
    assert sig.abs().max() <= 1
