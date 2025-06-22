import pandas as pd

from tradingbot.evaluation.metrics import calc_cagr, calc_max_drawdown, calc_sharpe


def test_calc_sharpe():
    # constant returns should yield zero sharpe (std=0)
    const = pd.Series([0.001] * 252)
    assert calc_sharpe(const) == 0.0

    # 1% mean, 1% std daily returns ~ sharpe sqrt(252)
    returns = pd.Series([0.01, 0.0] * 126)
    s = calc_sharpe(returns)
    assert s > 0


def test_max_drawdown():
    equity = pd.Series([1, 1.1, 0.9, 1.2])
    md = calc_max_drawdown(equity)
    assert abs(md + 0.1818) < 1e-2  # approx -18 %


def test_cagr():
    idx = pd.date_range("2020-01-01", "2021-01-01", freq="D")
    equity = pd.Series(1 + (idx.dayofyear / idx.dayofyear.max()), index=idx)
    # Roughly doubles in one year -> CAGR ~100%
    cagr = calc_cagr(equity)
    assert 0.95 < cagr < 1.05
