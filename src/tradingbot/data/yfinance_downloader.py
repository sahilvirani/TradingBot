# File: src/tradingbot/data/yfinance_downloader.py

from pathlib import Path
from typing import cast, Optional
import pandas as pd, yfinance as yf, time, yaml
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

CACHE_DIR = Path("data"); CACHE_DIR.mkdir(exist_ok=True)

def get_cache_path(symbol: str, interval: str) -> Path:
    """Return local cache path for a given symbol and interval."""
    return Path("data") / f"{symbol}_{interval}.csv"

def _dl(ticker, start, end):
    raw = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=True)
    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = raw.columns.get_level_values(0)
    return raw

def download_stock_data(ticker: str, *, start: str, end: Optional[str] = None, refresh=False, max_retry=5) -> pd.DataFrame:
    """
    Load from parquet cache. If file exists but is EMPTY, treat as stale and refresh.
    """
    # Use default end date if not provided
    if end is None:
        end = DEFAULT_END or pd.Timestamp.now().strftime("%Y-%m-%d")
    
    fp = CACHE_DIR / f"{ticker}_{start}_{end}.parquet"
    if fp.exists():
        df = pd.read_parquet(fp)
        if len(df) and not refresh:
            return df
        # cached but empty → force refresh
    for k in range(max_retry):
        df = _dl(ticker, start, end)
        if len(df):
            df.to_parquet(fp, index=True)
            return df
        wait = 2 ** k
        print(f"⚠️  {ticker} empty – retrying in {wait}s")
        time.sleep(wait)
    raise RuntimeError(f"{ticker} empty after {max_retry} attempts")
