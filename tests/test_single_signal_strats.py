from tradingbot.data.yfinance_downloader import download_stock_data
from tradingbot.strategy.runner import run_strategy


def test_single_signal_strategies_produce_signals():
    data = {"AAPL": download_stock_data("AAPL", start="2023-01-01", end="2024-01-01")}

    # Test mean reversion strategy
    mr_config = {"signals": ["mean_reversion"]}
    mr_signals = run_strategy(mr_config, data)
    assert "AAPL" in mr_signals
    assert len(mr_signals["AAPL"]) > 0

    # Test momentum strategy
    mom_config = {"signals": ["momentum"]}
    mom_signals = run_strategy(mom_config, data)
    assert "AAPL" in mom_signals
    assert len(mom_signals["AAPL"]) > 0
