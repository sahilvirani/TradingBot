# File: src/tradingbot/exec/alpaca_client.py
from __future__ import annotations

from alpaca.trading import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import MarketOrderRequest

from tradingbot.exec.creds import load_creds


class AlpacaClient:
    def __init__(self):
        creds = load_creds()
        alp = creds["alpaca"]
        paper = alp.get("paper", True)
        self.api = TradingClient(alp["key"], alp["secret"], paper=paper)

    def submit_order(self, symbol: str, qty: int, side: str, tif: str = "day"):
        """
        Submit a market order and return the API order object.
        side: 'buy' or 'sell'
        """
        order_side = OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL
        time_in_force = TimeInForce.DAY if tif.lower() == "day" else TimeInForce.GTC

        market_order_data = MarketOrderRequest(
            symbol=symbol, qty=qty, side=order_side, time_in_force=time_in_force
        )

        return self.api.submit_order(order_data=market_order_data)

    def current_position(self, symbol: str):
        try:
            return self.api.get_open_position(symbol)
        except Exception:  # no position
            return None
