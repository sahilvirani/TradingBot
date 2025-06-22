from __future__ import annotations

from typing import List, Tuple

import pandas as pd

from tradingbot.data.yfinance_downloader import download_stock_data
from tradingbot.evaluation.metrics import (
    calc_cagr,
    calc_max_drawdown,
    calc_sharpe,
)
from tradingbot.strategy.runner import backtest_with_atr, run_strategy

SECTOR_ETFS: List[str] = [
    "XLB",
    "XLC",
    "XLE",
    "XLF",
    "XLI",
    "XLK",
    "XLV",
    "XLU",
    "XLY",
    "XLRE",
]


def _simulate_simple_long_only(
    equity_init: float,
    universe: List[str],
    price_data: dict[str, pd.DataFrame],
    signal_dict: dict[str, pd.Series],
) -> Tuple[pd.Series, pd.Series]:
    """Very simple long-only backtest: equally weight *long* positions each day.

    Parameters
    ----------
    equity_init : float
        Starting capital.
    universe : list[str]
        Tickers in the universe.
    price_data : dict[str, DataFrame]
        Mapping ticker -> price history (must contain 'Close').
    signal_dict : dict[str, Series]
        Mapping ticker -> daily signal (1 = long, 0 = flat). Any negative values are
        ignored in this simple long-only simulation.

    Returns
    -------
    equity : pd.Series
        Daily portfolio value.
    daily_ret : pd.Series
        Daily portfolio returns.
    """
    # Use index from first ticker (assume aligned)
    dates = price_data[universe[0]].index
    # Align all Close series to the chosen date index (forward-fill gaps)
    aligned_close = {
        t: price_data[t]["Close"].reindex(dates).fillna(method="ffill")
        for t in universe
    }
    equity = pd.Series(equity_init, index=dates, dtype=float)
    daily_ret = pd.Series(0.0, index=dates, dtype=float)

    for i in range(1, len(dates)):
        date = dates[i]
        prev_date = dates[i - 1]

        # Determine tickers that were long over the holding period
        held = [t for t in universe if signal_dict[t].get(prev_date, 0) > 0]
        if held:
            rets = []
            for t in held:
                price_today = aligned_close[t][date]
                price_prev = aligned_close[t][prev_date]
                if pd.isna(price_today) or pd.isna(price_prev):
                    continue
                rets.append(price_today / price_prev - 1.0)

            avg_ret = sum(rets) / len(rets) if rets else 0.0
        else:
            avg_ret = 0.0

        daily_ret.iloc[i] = avg_ret
        equity.iloc[i] = equity.iloc[i - 1] * (1 + avg_ret)

    return equity, daily_ret


def benchmark_comparison(
    strategy_conf: dict,
    universe: List[str],
    *,
    risk_pct: float = 0.003,
    stop_mult: float = 2.0,
    use_atr_overlay: bool = True,
    return_dict: bool = False,
) -> dict | None:
    """Benchmark *strategy_conf*.

    Parameters
    ----------
    risk_pct : float
        Risk percentage passed to ATR overlay.
    stop_mult : float
        Multiplier for ATR overlay.
    use_atr_overlay : bool, default True
        If True, run the ATR‐sized simulator; otherwise fall back to equal-weight logic.
    return_dict : bool, default False
        If True, return metrics dictionary; else print and return None.
    """
    # Download price data for universe
    price_data = {ticker: download_stock_data(ticker) for ticker in universe}

    # ------------------------------------------------------------------
    # Build equity curve
    # ------------------------------------------------------------------
    if use_atr_overlay:
        # Use runner to generate signals first
        signals_dict = run_strategy(strategy_conf, price_data)

        equity = backtest_with_atr(
            {"signals_dict": signals_dict},
            price_data,
            start_equity=1_000_000,
            risk_pct=risk_pct,
            atr_window=14,
            stop_mult=stop_mult,
        )
        daily_ret = equity.pct_change().fillna(0)
    else:
        # fall back to equal-weight legacy path
        signals_dict = run_strategy(strategy_conf, price_data)
        equity, daily_ret = _simulate_simple_long_only(
            1.0, universe, price_data, signals_dict
        )

    # Build SPY equity curve over same dates
    dates = equity.index
    start_str = str(pd.Timestamp(dates[0]).date())
    end_str = str(pd.Timestamp(dates[-1]).date())
    spy_price = _load_spy_price(start_str, end_str)
    spy_price = spy_price.reindex(dates).fillna(method="ffill").fillna(method="bfill")
    spy_equity = spy_price / spy_price.iloc[0]
    spy_ret = spy_equity.pct_change().fillna(0)

    # Equal-weight sector ETF benchmark
    sector_prices = {
        etf: download_stock_data(etf, start=start_str, end=end_str)["Close"]
        .reindex(dates)
        .fillna(method="ffill")
        for etf in SECTOR_ETFS
    }
    sector_df = pd.DataFrame(sector_prices)
    sector_df = sector_df.fillna(method="ffill").fillna(method="bfill")
    sector_equity = sector_df.mean(axis=1) / sector_df.mean(axis=1).iloc[0]
    sector_ret = sector_equity.pct_change().fillna(0)

    # Metrics
    strat_sharpe = calc_sharpe(daily_ret)
    strat_cagr = calc_cagr(equity)
    strat_maxdd = calc_max_drawdown(equity)

    spy_sharpe = calc_sharpe(spy_ret)
    spy_cagr = calc_cagr(spy_equity)
    spy_maxdd = calc_max_drawdown(spy_equity)

    sec_sharpe = calc_sharpe(sector_ret)
    sec_cagr = calc_cagr(sector_equity)
    sec_maxdd = calc_max_drawdown(sector_equity)

    # Print headline metrics
    print(
        "Strategy: CAGR {cagr:.1f}%, Sharpe {sharpe:.2f}, MaxDD {mdd:.1f}%".format(
            cagr=strat_cagr * 100,
            sharpe=strat_sharpe,
            mdd=strat_maxdd * 100,
        )
    )
    print(
        "SPY:      CAGR {cagr:.1f}%, Sharpe {sharpe:.2f}, MaxDD {mdd:.1f}%".format(
            cagr=spy_cagr * 100,
            sharpe=spy_sharpe,
            mdd=spy_maxdd * 100,
        )
    )
    print(
        "Sector EW:CAGR {cagr:.1f}%, Sharpe {sharpe:.2f}, MaxDD {mdd:.1f}%".format(
            cagr=sec_cagr * 100,
            sharpe=sec_sharpe,
            mdd=sec_maxdd * 100,
        )
    )

    # Compare specific turbulent periods
    turbulent_periods = [
        ("2020-02-01", "2020-04-30"),
        ("2022-01-01", "2022-12-31"),
    ]
    excess_list: list[float] = []
    for start, end in turbulent_periods:
        start_date = pd.to_datetime(start)
        end_date = pd.to_datetime(end)
        # Use nearest valid indices if exact date unavailable
        strat_slice = equity.loc[start_date:end_date]
        spy_slice = spy_equity.loc[start_date:end_date]

        if strat_slice.empty or spy_slice.empty:
            continue

        strat_start_val, strat_end_val = strat_slice.iloc[0], strat_slice.iloc[-1]
        spy_start_val, spy_end_val = spy_slice.iloc[0], spy_slice.iloc[-1]

        strat_ret_period = float(strat_end_val / strat_start_val - 1.0)
        spy_ret_period = float(spy_end_val / spy_start_val - 1.0)
        excess = float(strat_ret_period - spy_ret_period)
        print(
            (
                f"{start} to {end}: Strategy {strat_ret_period*100:.1f}%, "
                f"SPY {spy_ret_period*100:.1f}%, Excess {excess*100:.1f}%"
            )
        )
        excess_list.append(excess)

    # Return dictionary if requested
    if return_dict:
        return {
            "sharpe": float(strat_sharpe),
            "max_dd": float(strat_maxdd),
            "excess_periods": int(sum(1 for v in excess_list if v > 0)),
            "trades": int((daily_ret != 0).sum()),
        }

    # also support external param
    return None


def _load_spy_price(start: str, end: str) -> pd.Series:
    """
    Return SPY daily CLOSE (price-only) so we compare like-with-like.
    """
    import yfinance as yf

    spy_data = yf.download("SPY", start=start, end=end, progress=False)
    spy_close = spy_data["Close"]
    spy_close.name = "SPY"
    return spy_close
