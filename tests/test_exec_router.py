# File: tests/test_exec_router.py
import pandas as pd
import pytest

# Try to import the executor, skip tests if alpaca dependency is missing
try:
    from tradingbot.exec.order_router import DailySignalExecutor

    EXEC_AVAILABLE = True
except ImportError:
    EXEC_AVAILABLE = False
    DailySignalExecutor = None  # type: ignore


class DummyAPI:
    def __init__(self):
        self.orders = []

    def submit_order(self, order_data):
        self.orders.append((order_data.symbol, order_data.qty, order_data.side))

        class Obj:
            id = "dummy"

        return Obj()


class DummyAlpacaClient:
    def __init__(self):
        self.api = DummyAPI()

    def submit_order(self, symbol: str, qty: int, side: str, tif: str = "day"):
        # Create a mock order_data object
        class MockOrderData:
            def __init__(self, symbol, qty, side):
                self.symbol = symbol
                self.qty = qty
                self.side = side

        order_data = MockOrderData(symbol, qty, side)
        return self.api.submit_order(order_data)


@pytest.mark.skipif(not EXEC_AVAILABLE, reason="Alpaca dependency not available")
def test_router_monkeypatch(monkeypatch, tmp_path):
    # Monkey-patch AlpacaClient with dummy
    monkeypatch.setattr("tradingbot.exec.order_router.AlpacaClient", DummyAlpacaClient)
    # Use tmp log path
    monkeypatch.setattr("tradingbot.exec.order_router.LOG_PATH", tmp_path / "log.csv")

    # Dummy data - need at least 14 days for ATR calculation
    idx = pd.date_range("2025-06-01", periods=20, freq="D")
    close_prices = [100 + i for i in range(20)]
    high_prices = [price + 1 for price in close_prices]
    low_prices = [price - 1 for price in close_prices]

    df = pd.DataFrame(
        {"Close": close_prices, "High": high_prices, "Low": low_prices}, index=idx
    )
    df.name = "AAPL"
    sig = pd.Series([0] * 19 + [1], index=idx)  # Only signal on last day

    ex = DailySignalExecutor()  # type: ignore
    ex.execute(df, sig)

    # Access orders through the mocked structure
    assert hasattr(ex.client, "api")
    assert hasattr(ex.client.api, "orders")
    assert len(ex.client.api.orders) == 1  # type: ignore
