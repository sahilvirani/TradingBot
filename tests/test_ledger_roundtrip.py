# File: tests/test_ledger_roundtrip.py

import pandas as pd

from tradingbot.strategy.runner import backtest_with_atr


def test_long_short_roundtrip():
    # Simple test: price goes down, short signal should profit
    idx = pd.date_range("2024-01-01", periods=2, freq="D")
    px = pd.Series([100.0, 50.0], index=idx)  # 50% drop
    df = pd.DataFrame(
        {
            "Open": px,
            "High": px + 1,
            "Low": px - 1,
            "Close": px,
            "Volume": 1000,
        }
    )
    price_data = {"FOO": df}

    # Test 1: Long-only signal (should lose money on 50% drop)
    long_sig = pd.Series([+1, 0], index=idx)
    long_signals = {"FOO": long_sig}

    long_equity = backtest_with_atr(
        {"signals_dict": long_signals},
        price_data,
        start_equity=100_000,
        risk_pct=0.01,  # 1% per trade
        atr_window=1,
        stop_mult=99,  # huge stop so it never hits
    )

    # Test 2: Short-only signal (should make money on 50% drop)
    short_sig = pd.Series([-1, 0], index=idx)
    short_signals = {"FOO": short_sig}

    short_equity = backtest_with_atr(
        {"signals_dict": short_signals},
        price_data,
        start_equity=100_000,
        risk_pct=0.01,  # 1% per trade
        atr_window=1,
        stop_mult=99,  # huge stop so it never hits
    )

    print(f"Long equity: {long_equity.tolist()}")
    print(f"Short equity: {short_equity.tolist()}")

    # If shorts work properly, short_equity should be MUCH higher than long
    # The short should profit from the 50% drop, while long loses money
    # If shorts are ignored, short_equity will be unchanged (100000)
    assert short_equity.iloc[-1] > 110_000, (
        f"Short strategy should profit significantly in falling market, "
        f"got {short_equity.iloc[-1]}"
    )
