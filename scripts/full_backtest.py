"""
Run the complete Sprint-19 trading engine on a chosen universe and
emit (1) a clean trade_log CSV   (2) an equity-curve CSV 
(3) a summary table that compares every strategy with SPY.
"""

import argparse, pandas as pd, numpy as np, yfinance as yf, os, sys
from pathlib import Path
from datetime import datetime
from typing import Dict
from tradingbot.data.sp500_top50 import get_top50_symbols
from tradingbot.config import strategies as STRATEGY_CONFIGS
from tradingbot.evaluation.benchmark_compare import benchmark_comparison

# ---------- helpers -------------------------------------------------
def calc_sharpe(ret, rf=0.0):
    ann = np.sqrt(252)
    excess = ret - rf/252
    return np.nan if excess.std()==0 else excess.mean()/excess.std()*ann

def max_drawdown(equity):
    roll_max = equity.cummax()
    dd = (equity/roll_max-1.0)
    return dd.min()

def load_spy(start, end, start_capital):
    spy_data = yf.download("SPY", start=start, end=end, progress=False)
    if isinstance(spy_data.columns, pd.MultiIndex):
        spy_data.columns = spy_data.columns.get_level_values(0)
    spy = spy_data["Close"]  # Use Close instead of Adj Close
    spy_ret = spy.pct_change().fillna(0)
    spy_equity = (1+spy_ret).cumprod() * start_capital
    return spy_equity, spy_ret

def get_top100_symbols():
    """Extend the top 50 to approximately 100 by adding more S&P 500 stocks."""
    # Start with top 50
    top50 = get_top50_symbols()
    
    # Add more S&P 500 stocks to get closer to 100
    additional_stocks = [
        "CSCO", "ACN", "VZ", "CRM", "NFLX", "INTU", "DHR", "TXN", "QCOM", "UPS",
        "HON", "LOW", "SCHW", "AMAT", "NEE", "PLTR", "SYK", "MDT", "GILD", "CVS",
        "T", "MO", "VRTX", "MMM", "FDX", "TJX", "DE", "BMY", "CB", "PLD",
        "SO", "DUK", "EXC", "XEL", "SRE", "AEP", "ITW", "APD", "EMR", "GE",
        "F", "GM", "DAL", "UAL", "CCL", "NCLH", "MGM", "LVS", "WYNN"
    ]
    
    return (top50 + additional_stocks)[:100]  # Return exactly 100 symbols

def backtest_with_trades(
    strategy_conf: dict,
    data: Dict[str, pd.DataFrame],
    start_equity: float = 1_000_000,
    *,
    risk_pct: float = 0.003,
    atr_window: int = 14,
    stop_mult: float = 2.0,
) -> tuple[pd.Series, pd.DataFrame]:
    """Modified backtest that returns both equity curve and trade log."""
    from tradingbot.strategy.runner import calc_atr, position_size, throttle_risk_pct
    
    if "signals_dict" not in strategy_conf:
        raise KeyError("strategy_conf must include 'signals_dict' for ATR back-test")

    signals_dict = strategy_conf["signals_dict"]
    
    # Get common date index
    dates = next(iter(data.values())).index
    
    # Pre-compute ATR for each ticker
    atr_map = {t: calc_atr(df, window=atr_window) for t, df in data.items()}
    
    equity = pd.Series(start_equity, index=dates, dtype=float)
    cash = start_equity
    
    positions = {t: 0 for t in data.keys()}
    entry_price = {t: np.nan for t in data.keys()}
    entry_dates = {t: None for t in data.keys()}  # Track entry dates separately
    
    # Trade log storage
    trades = []
    
    for i in range(1, len(dates)):
        today, prev_day = dates[i], dates[i - 1]
        
        # Check trailing-stop exits
        for t, qty in list(positions.items()):
            if qty == 0:
                continue
            price_today = data[t]["Close"].loc[today]
            atr_today_val = atr_map[t].get(today)
            if atr_today_val is None or pd.isna(atr_today_val):
                continue
            atr_today = float(atr_today_val)
            
            exit_triggered = False
            if qty > 0 and price_today < entry_price[t] - stop_mult * atr_today:
                exit_triggered = True
            elif qty < 0 and price_today > entry_price[t] + stop_mult * atr_today:
                exit_triggered = True
            
            if exit_triggered:
                # Record the trade
                pnl = qty * (price_today - entry_price[t])
                trades.append({
                    "ticker": t,
                    "entry_date": entry_dates[t] if entry_dates[t] is not None else prev_day,
                    "entry_price": entry_price[t],
                    "exit_date": today,
                    "exit_price": price_today,
                    "profit_or_loss": pnl,
                    "position_type": "buy" if qty > 0 else "short"
                })
                
                cash += qty * price_today
                positions[t] = 0
                entry_price[t] = float("nan")
                entry_dates[t] = None
        
        # Check for new entries
        for t, sig in signals_dict.items():
            if positions[t] != 0:
                continue
            
            sig_prev = sig.get(prev_day, 0)
            if sig_prev is not None and sig_prev != 0:
                atr_prev_val = atr_map[t].get(prev_day)
                if atr_prev_val is None or pd.isna(atr_prev_val):
                    continue
                atr_prev = float(atr_prev_val)
                
                adj_risk = throttle_risk_pct(risk_pct, prev_day)
                base_qty = position_size(equity.loc[prev_day], atr_prev, risk_pct=adj_risk)
                qty = int(base_qty * sig_prev)
                
                price_prev = data[t]["Close"].loc[prev_day]
                cost = abs(qty) * price_prev
                if cost <= cash or qty < 0:
                    if qty < 0:
                        cash += cost
                    else:
                        cash -= cost
                    positions[t] = qty
                    entry_price[t] = price_prev
                    entry_dates[t] = prev_day  # Store entry date properly
        
        # Mark-to-market
        portfolio_val = cash + sum(
            positions[t] * data[t]["Close"].loc[today]
            for t in positions if positions[t] != 0
        )
        equity.iloc[i] = portfolio_val
    
    # Close any remaining positions at the end
    final_date = dates[-1]
    for t, qty in positions.items():
        if qty != 0:
            price_final = data[t]["Close"].loc[final_date]
            pnl = qty * (price_final - entry_price[t])
            trades.append({
                "ticker": t,
                "entry_date": entry_dates[t] if entry_dates[t] is not None else final_date,
                "entry_price": entry_price[t],
                "exit_date": final_date,
                "exit_price": price_final,
                "profit_or_loss": pnl,
                "position_type": "buy" if qty > 0 else "short"
            })
    
    trade_df = pd.DataFrame(trades)
    return equity, trade_df

# ---------- main runner ---------------------------------------------
def run_all(start, end, capital, risk_pct, universe):
    from tradingbot.data.yfinance_downloader import download_stock_data
    from tradingbot.strategy.runner import run_strategy
    from typing import Dict
    
    out_dir = Path("out"); out_dir.mkdir(exist_ok=True)
    all_trades, eq_curves, rows = [], {}, []
    
    print(f"📊 Downloading data for {len(universe)} symbols from {start} to {end}...")
    
    # Download data with proper date filtering
    price_data = {}
    for ticker in universe:
        try:
            df = download_stock_data(ticker, start=start, end=end, refresh=False)  # Use cached data
            # Filter to exact date range
            df = df.loc[start:end]
            if len(df) > 0:
                price_data[ticker] = df
        except Exception as e:
            print(f"⚠️  Failed to download {ticker}: {e}")
    
    print(f"✅ Successfully downloaded {len(price_data)} symbols")

    for cfg in STRATEGY_CONFIGS:
        name = cfg.get("name", "unnamed")
        print(f"▶ Running strategy: {name}")
        cfg_use = cfg.copy()
        cfg_use.update({"start_date": start, "end_date": end})

        try:
            # Run strategy to get signals
            signals_dict = run_strategy(cfg_use, price_data)
            
            # Run backtest with trade capture
            equity, trades = backtest_with_trades(
                {"signals_dict": signals_dict},
                price_data,
                start_equity=capital,
                risk_pct=risk_pct,
                atr_window=14,
                stop_mult=2.0,
            )
            
            # Filter equity to date range
            equity = equity.loc[start:end]
            
            trades["strategy"] = name
            all_trades.append(trades)
            eq_curves[name] = equity
            
            # Calculate metrics
            returns = equity.pct_change().fillna(0)
            sharpe = calc_sharpe(returns)
            max_dd = max_drawdown(equity)
            total_return_pct = (equity.iloc[-1]/capital - 1) * 100
            
            win_rate = (trades["profit_or_loss"] > 0).mean() * 100 if len(trades) > 0 else 0
            avg_trade = trades["profit_or_loss"].mean() if len(trades) > 0 else 0
            
            rows.append({
                "name": name,
                "sharpe": sharpe,
                "max_dd": max_dd,
                "total_return_%": total_return_pct,
                "win_rate_%": win_rate,
                "avg_trade_$": avg_trade,
                "num_trades": len(trades),
            })
            
            print(f"  ✅ {name}: {total_return_pct:.1f}% return, {len(trades)} trades")
            
        except Exception as e:
            print(f"  ❌ Error running strategy {name}: {e}")
            rows.append({
                "name": name,
                "sharpe": 0,
                "max_dd": 0,
                "total_return_%": 0,
                "win_rate_%": 0,
                "avg_trade_$": 0,
                "num_trades": 0,
            })

    # Combine and save results
    if all_trades:
        trade_log = pd.concat(all_trades, ignore_index=True)
    else:
        trade_log = pd.DataFrame(columns=["ticker","entry_date","entry_price","exit_date","exit_price","profit_or_loss","strategy"])
    
    tag = f"{start}_{end}"
    trade_log.to_csv(out_dir/f"trade_log_{tag}.csv", index=False)
    print(f"💾 Saved trade log: {len(trade_log)} trades")

    if eq_curves:
        equity = pd.concat(eq_curves, axis=1)
        equity.to_csv(out_dir/f"equity_{tag}.csv")
        print(f"💾 Saved equity curves: {len(equity)} days")

    # Benchmark comparison
    try:
        spy_eq, spy_ret = load_spy(start, end, capital)
        spy_sharpe = calc_sharpe(spy_ret)
        spy_dd = max_drawdown(spy_eq)
        spy_return_pct = (spy_eq.iloc[-1]/capital - 1)*100
    except Exception as e:
        print(f"⚠️  Error loading SPY data: {e}")
        spy_sharpe = 0
        spy_dd = 0
        spy_return_pct = 0

    # Summary table
    df = pd.DataFrame(rows).set_index("name")
    df["spy_ret_%"] = spy_return_pct
    df["alpha_%"] = df["total_return_%"] - df["spy_ret_%"]
    
    print("\n" + "="*60)
    print("🏆 PERFORMANCE SUMMARY vs SPY")
    print("="*60)
    cols_to_show = ["total_return_%","alpha_%","sharpe","max_dd","win_rate_%","num_trades"]
    print(df[cols_to_show].round(2))
    print(f"\n📊 SPY Benchmark: {spy_return_pct:.1f}% return | Sharpe {spy_sharpe:.2f} | Max DD {spy_dd:.1%}")
    print("="*60)

    df.to_csv(out_dir/f"summary_{tag}.csv")

# ---------- CLI -------------------
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", required=True)
    ap.add_argument("--end", required=True)
    ap.add_argument("--capital", type=float, default=100_000)
    ap.add_argument("--risk_pct", type=float, default=0.0006)
    ap.add_argument("--top_n", type=int, default=100,
        help="Number of tickers from SP-500 list (<=100 keeps runtime reasonable).")
    args = ap.parse_args()

    universe = get_top100_symbols()[: args.top_n]
    run_all(args.start, args.end, args.capital, args.risk_pct, universe) 