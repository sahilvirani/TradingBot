# File: tests/test_is_oos_eval.py
from tradingbot.backtest.is_oos_eval import run_is_oos_test


def test_is_oos_eval_small():
    res = run_is_oos_test(symbols=["AAPL", "MSFT"], oos_end="2025-02-01")
    # ensure we got OOS metrics
    assert not res.empty and "OOS_Sharpe" in res.columns
