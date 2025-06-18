# File: src/tradingbot/backtest/vbt_runner.py

from __future__ import annotations

import pandas as pd
import vectorbt as vbt

DEFAULT_FEES_PCT = 0.0005  # 5 bp slippage
DEFAULT_COMM_PER_SHARE = 0.005  # $0.005 commission


def run_backtest(
    price: pd.Series,
    signal: pd.Series,
    fees_pct: float = DEFAULT_FEES_PCT,
    comm_per_share: float = DEFAULT_COMM_PER_SHARE,
) -> vbt.Portfolio:
    """
    Run a simple back-test using vectorbt.

    Args
    ----
    price   : Close price Series (index = datetime)
    signal  : Position signal Series {-1,0,1} aligned with price
    fees_pct: Proportional slippage per trade (both sides)
    comm_per_share: Fixed commission per share

    Returns
    -------
    vbt.Portfolio object with performance stats
    """
    if not price.index.equals(signal.index):
        signal = signal.reindex(price.index).fillna(0)

    entries = signal.diff().fillna(0) > 0  # where we go from ≤0 to 1
    exits = signal.diff() < 0  # where we drop from ≥0 to 0/-1

    pf = vbt.Portfolio.from_signals(
        close=price,
        entries=entries,
        exits=exits,
        short_entries=signal.diff() < 0,  # opening shorts
        short_exits=signal.diff() > 0,  # closing shorts
        fees=fees_pct,
        fixed_fees=comm_per_share,
        init_cash=1_000_000,  # $1 M starting equity
        freq="D",
    )
    return pf
