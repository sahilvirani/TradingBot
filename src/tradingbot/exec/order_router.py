# File: src/tradingbot/exec/order_router.py
from datetime import datetime
from pathlib import Path

import pandas as pd

from tradingbot.exec.alpaca_client import AlpacaClient
from tradingbot.risk.position_sizer import atr_position_size

LOG_PATH = Path("data/fill_log.csv")


class DailySignalExecutor:
    def __init__(self):
        self.client = AlpacaClient()

    def execute(self, df: pd.DataFrame, signal: pd.Series):
        """
        For today's signal {-1,0,1}, send market order at market open.
        Assumes df index is daily and last row = today.
        """
        today = df.index[-1]  # type: ignore
        if hasattr(today, "date"):
            today = today.date()  # type: ignore
        price_today = df["Close"].iloc[-1]
        sig = int(signal.iloc[-1])

        if sig == 0:
            return  # nothing to do

        side = "buy" if sig > 0 else "sell"
        qty = int(abs(atr_position_size(df).iloc[-1]))
        if qty == 0:
            return

        # Get symbol name from DataFrame name or use a default
        symbol = getattr(df, "name", "UNKNOWN")

        order = self.client.submit_order(symbol, qty, side)
        order_id = getattr(order, "id", "unknown")

        LOG_PATH.parent.mkdir(exist_ok=True)
        log_data = pd.DataFrame(
            {
                "utc_time": [datetime.utcnow()],
                "symbol": [symbol],
                "side": [side],
                "qty": [qty],
                "price": [price_today],
                "order_id": [order_id],
            }
        )
        log_data.to_csv(LOG_PATH, mode="a", index=False, header=not LOG_PATH.exists())
