# File: tests/test_signals_momentum.py

from tradingbot.data.yfinance_downloader import download_stock_data
from tradingbot.signals.momentum import generate_mom_signal


def test_momentum_signal():
    df = download_stock_data("AAPL", start="2023-01-01")

    sig_simple = generate_mom_signal(df, use_vol_adjust=False)
    sig_adj = generate_mom_signal(df, use_vol_adjust=True)

    # shape matches
    assert len(sig_simple) == len(df)
    assert len(sig_adj) == len(df)

    # signal values are restricted to {-1,0,1}
    assert sig_simple.isin({-1, 0, 1}).all()
    assert sig_adj.isin({-1, 0, 1}).all()

    # there should be at least one non-zero signal
    assert sig_simple.abs().sum() > 0
    assert sig_adj.abs().sum() > 0
