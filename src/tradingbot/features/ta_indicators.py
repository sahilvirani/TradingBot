import pandas as pd
import ta


def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add RSI, MACD, and ATR to price dataframe.

    The function is robust to CSVs saved by yfinance which include leading
    metadata rows (Price/Ticker/Date). Columns are coerced to numeric before
    indicator computation.
    """
    df = df.copy()

    # Ensure price columns are numeric
    numeric_cols = [
        c for c in ["Open", "High", "Low", "Close", "Volume"] if c in df.columns
    ]
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")

    # Some cached CSVs include header rows ("Price", "Ticker", "Date").
    # Keep only rows whose index parses to a datetime.
    mask = pd.to_datetime(df.index, errors="coerce").notna()
    df = df.loc[mask].copy()
    df.index = pd.to_datetime(df.index)

    # --- Technical indicators -------------------------------------------------
    # `ta` library doesn't ship with type stubs, so we silence the type checker
    df["rsi_14"] = ta.momentum.RSIIndicator(  # type: ignore[attr-defined]
        close=df["Close"], window=14
    ).rsi()

    macd = ta.trend.MACD(close=df["Close"])  # type: ignore[attr-defined]
    df["macd_diff"] = macd.macd_diff()

    atr = ta.volatility.AverageTrueRange(  # type: ignore[attr-defined]
        high=df["High"], low=df["Low"], close=df["Close"], window=14
    )
    df["atr_14"] = atr.average_true_range()

    return df  # type: ignore[return-value]
