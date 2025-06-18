from typing import cast

import pandas as pd

from tradingbot.data.yfinance_downloader import download_stock_data
from tradingbot.features.base_features import (
    compute_daily_returns,
    compute_rolling_zscore,
)
from tradingbot.features.ta_indicators import add_technical_indicators


def test_feature_generation():
    df = download_stock_data("AAPL", interval="1d", start="2023-01-01")
    df = add_technical_indicators(df)
    df["returns"] = compute_daily_returns(df)
    close_series = cast(pd.Series, df["Close"])  # explicit cast for type checker
    df["zscore"] = compute_rolling_zscore(close_series)

    assert "rsi_14" in df.columns
    assert "macd_diff" in df.columns
    assert "atr_14" in df.columns
    assert bool(df["returns"].notna().all())  # type: ignore[arg-type]
    assert df["zscore"].notna().sum() > 0  # some values should be defined
