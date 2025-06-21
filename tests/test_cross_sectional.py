import pandas as pd

from tradingbot.signals.cross_sectional import rank_top_n_df


def test_rank_top_n_df_basic():
    data = pd.DataFrame(
        {
            "StockA": [0.05, -0.02],
            "StockB": [0.10, 0.03],
            "StockC": [-0.04, -0.05],
        },
        index=pd.to_datetime(["2023-01-01", "2023-01-02"]),
    )

    top1 = rank_top_n_df(data, n=1, highest=True)
    assert top1.loc["2023-01-01"].sum() == 1
    assert top1.loc["2023-01-01", "StockB"] == 1
    assert top1.loc["2023-01-02", "StockB"] == 1

    bottom1 = rank_top_n_df(data, n=1, highest=False)
    assert bottom1.loc["2023-01-01", "StockC"] == 1
    assert bottom1.loc["2023-01-02", "StockC"] == 1
