import pandas as pd

from tradingbot.evaluation.success_report import evaluate_all


def test_success_report_runs():
    df = evaluate_all()
    assert (df["trades"] > 0).any()
    for col in ["sharpe", "max_dd", "excess_periods"]:
        assert col in df.columns
    finite = df["sharpe"].replace([float("inf"), float("-inf")], pd.NA).dropna()
    assert finite.size > 0
