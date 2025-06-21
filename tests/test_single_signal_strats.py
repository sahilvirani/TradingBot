from tradingbot.data.yfinance_downloader import download_stock_data
from tradingbot.strategy.runner import run_strategy


def test_single_signal_strategies_produce_signals():
    data = {"AAPL": download_stock_data("AAPL", start="2023-01-01")}

    mr_conf = {"signals": ["mean_reversion"], "allowed_regimes": ["calm", "normal"]}
    mom_conf = {
        "signals": ["momentum"],
        "allowed_regimes": ["calm", "normal", "turbulent"],
    }

    mr_signals = run_strategy(mr_conf, data)
    mom_signals = run_strategy(mom_conf, data)

    # Ensure signals are generated and contain at least some non-zero entries
    assert mr_signals["AAPL"].abs().sum() > 0
    assert mom_signals["AAPL"].abs().sum() > 0
