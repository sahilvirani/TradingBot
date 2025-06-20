# File: src/tradingbot/monitor/heartbeat.py
from datetime import datetime, time

from tradingbot.monitor.prom import drawdown_gauge, open_pos_gauge, pnl_gauge
from tradingbot.monitor.slack_alerts import send_slack_message


def update_metrics(pnl_pct: float, dd_pct: float, open_pos: int):
    pnl_gauge.set(pnl_pct)
    drawdown_gauge.set(dd_pct)
    open_pos_gauge.set(open_pos)

    # Alert if drawdown > 5 %
    if dd_pct <= -5:
        send_slack_message(f"⚠️ Draw-down alert: {dd_pct:.2f}%")


def daily_close_summary(equity: float, pnl_pct: float, dd_pct: float):
    now = datetime.now().time()
    if now >= time(16, 10):  # after US market close
        message = (
            f"Daily summary — Equity: ${equity:,.0f} | "
            f"PnL: {pnl_pct:.2f}% | DD: {dd_pct:.2f}%"
        )
        send_slack_message(message)
