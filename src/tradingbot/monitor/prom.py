# File: src/tradingbot/monitor/prom.py
from prometheus_client import Gauge, start_http_server

pnl_gauge = Gauge("bot_equity_pct", "Cumulative return (%)")
drawdown_gauge = Gauge("bot_drawdown_pct", "Current drawdown (%)")
open_pos_gauge = Gauge("bot_open_positions", "Number of open positions")


def start_prom_server(port: int = 8000):
    start_http_server(port)
