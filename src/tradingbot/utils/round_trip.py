import pandas as pd

def fills_to_round_trips(fills: pd.DataFrame) -> pd.DataFrame:
    """
    Pair BUY–SELL (or SELL–BUY) to compute realised PnL.
    Assumes each position is fully closed in a single opposite-side fill.
    """
    out = []
    open_pos = {}
    
    # Ensure we have the required columns from the backtest fills
    required_cols = ['symbol', 'open_time', 'open_price', 'close_time', 'close_price', 'pnl', 'side']
    if not all(col in fills.columns for col in required_cols):
        # If fills already has the right format, return as-is
        if all(col in fills.columns for col in ['entry_date', 'entry_price', 'exit_date', 'exit_price', 'profit_or_loss']):
            return fills
        raise ValueError(f"Expected columns {required_cols} in fills DataFrame")
    
    for _, row in fills.sort_values("open_time").iterrows():
        # Convert the backtest fill format to round-trip format
        out.append({
            "ticker": row["symbol"],
            "entry_date": row["open_time"],
            "entry_price": row["open_price"],
            "exit_date": row["close_time"],
            "exit_price": row["close_price"],
            "profit_or_loss": row["pnl"],
            "strategy": row.get("strategy", "Unknown")
        })
    
    return pd.DataFrame(out) 