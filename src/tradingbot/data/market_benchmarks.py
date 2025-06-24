from .yfinance_downloader import download_stock_data
from datetime import datetime
from functools import lru_cache

def get_spy(start, end):
    return download_stock_data("SPY", start=start, end=end)["Close"]

def get_vix(start="2010-01-01", end=None):
    if end is None:
        end = datetime.now().strftime("%Y-%m-%d")
    return download_stock_data("^VIX", start=start, end=end)["Close"]

@lru_cache(maxsize=1)
def get_spy_series(start="2010-01-01", end=None):
    if end is None:
        end = datetime.now().strftime("%Y-%m-%d")
    return download_stock_data("SPY", start=start, end=end)["Close"]

@lru_cache(maxsize=1)
def get_vix_series(start="2010-01-01", end=None):
    if end is None:
        end = datetime.now().strftime("%Y-%m-%d")
    return download_stock_data("^VIX", start=start, end=end)["Close"] 