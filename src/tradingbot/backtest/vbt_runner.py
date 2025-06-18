# File: src/tradingbot/backtest/vbt_runner.py

from __future__ import annotations

import pandas as pd
import vectorbt as vbt

from tradingbot.risk.position_sizer import atr_position_size

DEFAULT_FEES_PCT = 0.0005  # 5 bp slippage
DEFAULT_COMM_PER_SHARE = 0.005  # $0.005 commission


def run_backtest(
    price: pd.Series,
    signal: pd.Series,
    df_full: pd.DataFrame | None = None,
    fees_pct: float = DEFAULT_FEES_PCT,
    comm_per_share: float = DEFAULT_COMM_PER_SHARE,
) -> vbt.Portfolio:
    """
    If df_full is provided, ATR position sizing is applied;
    otherwise a constant 1 share is traded.

    Args
    ----
    price   : Close price Series (index = datetime)
    signal  : Position signal Series {-1,0,1} aligned with price
    df_full : DataFrame for ATR position sizing
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
    short_entries = signal.diff() < 0  # opening shorts
    short_exits = signal.diff() > 0  # closing shorts

    if df_full is not None:
        size = atr_position_size(df_full).reindex(price.index).ffill()
    else:
        size = 1  # fallback constant size

    pf = vbt.Portfolio.from_signals(
        close=price,
        entries=entries,
        exits=exits,
        short_entries=short_entries,
        short_exits=short_exits,
        size=size,
        fees=fees_pct,
        fixed_fees=comm_per_share,
        init_cash=1_000_000,  # $1 M starting equity
        freq="D",
    )
    return pf
