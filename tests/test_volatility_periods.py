from tradingbot.data.yfinance_downloader import download_stock_data
from tradingbot.signals.mean_reversion import generate_mr_signal


def test_strategy_trades_in_2020_crash():
    df = download_stock_data("SPY", start="2020-02-01", end="2020-04-30", refresh=False)
    sig = generate_mr_signal(df)
    assert sig.abs().sum() > 0, "No trades generated during 2020 crash period!"
