# File: tests/test_signals_mr.py

from tradingbot.data.yfinance_downloader import download_stock_data
from tradingbot.signals.mean_reversion import generate_mr_long_short, generate_mr_signal


def test_mr_signal_shapes():
    df = download_stock_data("AAPL", start="2023-01-01")
    long_only = generate_mr_signal(df)
    long_short = generate_mr_long_short(df)

    assert len(long_only) == len(df)
    assert long_only.isin({0, 1}).all()
    assert long_short.isin({-1, 0, 1}).all()
