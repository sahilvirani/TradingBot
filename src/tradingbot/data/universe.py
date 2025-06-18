# File: src/tradingbot/data/universe.py

DEFAULT_UNIVERSE = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"]


def get_universe(symbols: list[str] | None = None) -> list[str]:
    """Return list of tickers to test."""
    return symbols or DEFAULT_UNIVERSE
