# File: tests/test_walkforward_mc.py

from tradingbot.backtest.walkforward import walk_forward_optimize
from tradingbot.data.yfinance_downloader import download_stock_data
from tradingbot.risk.monte_carlo import mc_var_es, monte_carlo_paths


def test_walkforward_and_mc():
    df = download_stock_data("AAPL", start="2022-01-03", end="2024-01-01")
    grid = dict(enter_thresh=[-0.5, -1.0], exit_thresh=[0.0], window=[20, 40])
    wf = walk_forward_optimize(df, grid, is_days=252, oos_days=63)
    assert not wf.empty and "Sharpe" in wf.columns

    # Monte-Carlo on the full equity curve of last fold
    last_fold_ret = (1 + df["Close"].pct_change().fillna(0)).iloc[-252:] - 1
    paths = monte_carlo_paths(last_fold_ret)
    stats = mc_var_es(paths)
    assert "VaR" in stats and "ES" in stats
