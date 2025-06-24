import argparse, pandas as pd, numpy as np, yfinance as yf, time
from pathlib import Path
from tradingbot.data.yfinance_downloader import download_stock_data
from tradingbot.data.sp500_top50 import get_top100_symbols
from tradingbot.data.market_benchmarks import get_spy_series, get_vix_series
from tradingbot.config import strategies
from tradingbot.strategy.runner import run_strategy, backtest_with_atr
from tradingbot.utils.round_trip import fills_to_round_trips

def sharpe(r): return (r.mean()/r.std())*np.sqrt(252) if r.std() > 0 else 0.0
def maxdd(eq): return (eq/eq.cummax()-1).min()

def main(args):
    # Pre-load SPY and VIX series once to eliminate repeated downloads
    print("Pre-loading SPY and VIX series...")
    SPY_SERIES = get_spy_series()
    VIX_SERIES = get_vix_series() 
    print(f"✓ SPY: {len(SPY_SERIES)} rows, VIX: {len(VIX_SERIES)} rows")
    
    # Use top 100 S&P 500 stocks for more comprehensive simulation
    universe = get_top100_symbols()
    print(f"Downloading data for {len(universe)} symbols...")
    
    price_data = {}
    failed_count = 0
    
    # Download in smaller batches with delays to avoid rate limiting
    batch_size = 10
    for i in range(0, len(universe), batch_size):
        batch = universe[i:i+batch_size]
        print(f"Processing batch {i//batch_size + 1}/{(len(universe)-1)//batch_size + 1}: {batch[:3]}{'...' if len(batch) > 3 else ''}")
        
        for ticker in batch:
            try:
                df = download_stock_data(ticker, start=args.start, end=args.end)
                if len(df) > 0:
                    price_data[ticker] = df
                    print(f"✓ {ticker}: {len(df)} rows")
                else:
                    print(f"✗ {ticker}: empty data")
                    failed_count += 1
            except Exception as e:
                print(f"✗ {ticker}: {e}")
                failed_count += 1
        
        # Brief delay between batches to respect rate limits
        if i + batch_size < len(universe):
            time.sleep(2)
    
    successful_count = len(price_data)
    print(f"\n=== DATA SUMMARY ===")
    print(f"✓ Successfully loaded: {successful_count}/{len(universe)} symbols")
    print(f"✗ Failed: {failed_count}/{len(universe)} symbols")
    print(f"Coverage: {successful_count/len(universe)*100:.1f}%")

    if successful_count == 0:
        print("❌ No data loaded. Exiting.")
        return

    log_rows, eq_curves, trades_all = [], {}, []
    
    for cfg in strategies:
        strategy_name = cfg.get("name", "Unknown")
        print(f"\nRunning strategy: {strategy_name}")
        
        try:
            # Generate signals with cached SPY/VIX series to eliminate downloads
            signals_dict = run_strategy(
                cfg, 
                price_data,
                spy_series=SPY_SERIES,
                vix_series=VIX_SERIES,
            )
            
            # Run backtest with fills and cached VIX series
            equity, fills = backtest_with_atr(
                {"signals_dict": signals_dict},
                price_data,
                start_equity=args.capital,
                risk_pct=args.risk,
                atr_window=14,
                stop_mult=2.0,
                return_fills=True,
                vix_series=VIX_SERIES,
            )
            
            eq_curves[strategy_name] = equity
            fills["strategy"] = strategy_name
            
            # Convert fills to round-trip trades
            round_trips = fills_to_round_trips(fills)
            trades_all.append(round_trips)

            r = equity.pct_change().dropna()
            log_rows.append({
                "name": strategy_name,
                "total_%": (equity.iloc[-1]/equity.iloc[0]-1)*100,
                "sharpe":  round(sharpe(r), 2),
                "max_dd":  round(maxdd(equity), 3),
                "trades":  len(round_trips)
            })
            print(f"✓ {strategy_name}: {len(round_trips)} trades, Final: ${equity.iloc[-1]:,.0f}")
            
        except Exception as e:
            print(f"✗ {strategy_name}: {e}")
            import traceback
            traceback.print_exc()
            log_rows.append({
                "name": strategy_name,
                "total_%": 0,
                "sharpe": 0,
                "max_dd": 0,
                "trades": 0
            })

    # Save results
    out = Path("out"); out.mkdir(exist_ok=True)
    tag = f"{args.start}_{args.end}"
    
    if trades_all:
        all_trades = pd.concat(trades_all, ignore_index=True)
        all_trades.to_csv(out/f"trade_log_{tag}.csv", index=False)
        print(f"\nSaved {len(all_trades)} trades to trade_log_{tag}.csv")
    
    if eq_curves:
        equity_df = pd.concat(eq_curves, axis=1)
        equity_df.to_csv(out/f"equity_{tag}.csv")
        print(f"Saved equity curves to equity_{tag}.csv")

    # Add SPY benchmark using pre-loaded cached data
    try:
        dates = equity.index if 'equity' in locals() else pd.date_range(args.start, args.end, freq='D')
        spy_slice = SPY_SERIES.reindex(dates).ffill()
        spy_r = spy_slice.pct_change().dropna()
        spy_eq = (1+spy_r).cumprod()*args.capital
        spy_row = {"name":"SPY",
                   "total_%": (spy_eq.iloc[-1]/spy_eq.iloc[0]-1)*100,
                   "sharpe":  round(sharpe(spy_r), 2),
                   "max_dd":  round(maxdd(spy_eq), 3),
                   "trades": 0}
        log_rows.append(spy_row)
        print(f"✓ SPY benchmark: {spy_row['total_%']:.1f}% total return")
    except Exception as e:
        print(f"⚠️  SPY load failed: {e}")
    
    # Create summary table
    table = pd.DataFrame(log_rows).set_index("name")
    table.to_csv(out/f"summary_{tag}.csv")
    print("\n" + "="*60)
    print("PERFORMANCE SUMMARY")
    print("="*60)
    print(table.round(2))
    print("="*60)
    print(f"Universe: {successful_count} stocks | Period: {args.start} to {args.end}")
    
    # Calculate annualized return for winner
    if len(table) > 0 and 'total_%' in table.columns:
        years = (pd.to_datetime(args.end) - pd.to_datetime(args.start)).days / 365.25
        best_strat = table.loc[table['total_%'].idxmax()]
        annualized = (1 + best_strat['total_%']/100)**(1/years) - 1
        print(f"Best strategy annualized return: {annualized*100:.1f}%/year")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2019-01-01")
    ap.add_argument("--end",   default="2025-01-01")  # Extended to 2025
    ap.add_argument("--capital", type=float, default=100_000)
    ap.add_argument("--risk", type=float, default=0.0006)
    main(ap.parse_args()) 