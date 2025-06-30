# File: tests/test_signals_momentum.py

from tradingbot.data.yfinance_downloader import download_stock_data
from tradingbot.signals.momentum import generate_mom_signal


def test_momentum_signal():
    df = download_stock_data("AAPL", start="2023-01-01", end="2024-01-01")
    sig = generate_mom_signal(df)

    # assert basic expectations
    assert len(sig) == len(df)
    assert sig.abs().max() <= 1

    # shape matches
    assert len(sig) == len(df)

    # signal values are restricted to {-1,0,1}
    assert sig.isin({-1, 0, 1}).all()

    # there should be at least one non-zero signal
    assert sig.abs().sum() > 0
