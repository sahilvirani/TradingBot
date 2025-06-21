# File: src/tradingbot/data/yfinance_downloader.py

from pathlib import Path
from typing import cast

import pandas as pd
import yaml
import yfinance as yf
from loguru import logger

# Load default backtest date range from config
_cfg_path = Path("config/tradingbot.yaml")
if _cfg_path.exists():
    _cfg = yaml.safe_load(_cfg_path.read_text()) or {}
    _bt_cfg = _cfg.get("backtest", {})
    DEFAULT_START = _bt_cfg.get("start_date", "2015-01-01")
    DEFAULT_END = _bt_cfg.get("end_date", None)
else:
    DEFAULT_START = "2015-01-01"
    DEFAULT_END = None


def get_cache_path(symbol: str, interval: str) -> Path:
    """Return local cache path for a given symbol and interval."""
    return Path("data") / f"{symbol}_{interval}.csv"


def download_stock_data(
    symbol: str,
    interval: str = "1d",
    start: str = DEFAULT_START,
    end: str | None = DEFAULT_END,
    refresh: bool = False,
) -> pd.DataFrame:
    """Download stock data and cache to CSV unless refresh=True.

    If `end` is None, data is downloaded up to today.
    """
    path = get_cache_path(symbol, interval)

    if path.exists() and not refresh:
        logger.info(f"Using cached data: {path}")
        # Skip rows 1 and 2 which contain ticker names and empty Date row
        df = pd.read_csv(path, index_col=0, parse_dates=True, skiprows=[1, 2])
        # Set proper index name
        df.index.name = "Date"
        # Ensure numeric columns are properly typed
        numeric_cols = ["Open", "High", "Low", "Close", "Volume"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        return df

    logger.info(f"{'Refreshing' if refresh else 'Downloading'} {symbol}...")
    df = cast(
        pd.DataFrame,
        yf.download(symbol, interval=interval, start=start, end=end),
    )

    # Handle multi-level columns from yfinance
    if isinstance(df.columns, pd.MultiIndex):
        # Flatten multi-level columns by taking the first level
        # (e.g., 'Close' from ('Close', 'MSFT'))
        df.columns = df.columns.get_level_values(0)

    # Create the data directory if it doesn't exist
    path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(path)
    logger.info(f"Saved to cache: {path}")
    return df
