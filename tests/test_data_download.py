# File: tests/test_data_download.py

import pandas as pd

from tradingbot.data.yfinance_downloader import download_stock_data


def test_download_and_cache():
    df = download_stock_data("AAPL", start="2023-01-01")
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "Close" in df.columns
