# File: src/tradingbot/data/yfinance_downloader.py

from pathlib import Path

import pandas as pd
import yfinance as yf
from loguru import logger


def get_cache_path(symbol: str, interval: str) -> Path:
    """Return local cache path for a given symbol and interval."""
    return Path("data") / f"{symbol}_{interval}.csv"


def download_stock_data(
    symbol: str, interval: str = "1d", start: str = "2020-01-01", refresh: bool = False
) -> pd.DataFrame:
    """Download stock data and cache to CSV unless refresh=True."""
    path = get_cache_path(symbol, interval)

    if path.exists() and not refresh:
        logger.info(f"Using cached data: {path}")
        return pd.read_csv(path, index_col=0, parse_dates=True)

    logger.info(f"{'Refreshing' if refresh else 'Downloading'} {symbol}...")
    df = yf.download(symbol, interval=interval, start=start)
    df.to_csv(path)
    logger.info(f"Saved to cache: {path}")
    return df
