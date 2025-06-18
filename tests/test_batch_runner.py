# File: tests/test_batch_runner.py

from tradingbot.backtest.aggregate import aggregate_metrics
from tradingbot.backtest.batch_runner import grid_search_batch


def test_batch_runner_multi_ticker():
    df = grid_search_batch(start="2023-01-03", universe=["AAPL", "MSFT"])
    assert {"Symbol", "Sharpe", "enter_thresh", "window"}.issubset(df.columns)
    agg = aggregate_metrics(df)
    assert not agg.empty
    # Ensure at least one parameter set has positive mean Sharpe
    assert (agg["Sharpe"] > 0).any()
