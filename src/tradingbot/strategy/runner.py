from __future__ import annotations

from typing import Dict, List

import numpy as np
import pandas as pd

from tradingbot.risk.atr import calc_atr, position_size
from tradingbot.risk.vix_filter import throttle_risk_pct
from tradingbot.signals.cross_sectional import (
    compute_return_matrix,
    rank_top_n_df,
    universe_momentum_ok,
)
from tradingbot.signals.mean_reversion import generate_mr_signal
from tradingbot.signals.momentum import generate_mom_signal
from tradingbot.signals.regime_filter import apply_regime_filter


def _gen_signal_by_type(signal_type: str, df: pd.DataFrame) -> pd.Series:
    """Helper to generate a signal Series given signal type string."""
    if signal_type == "mean_reversion":
        return generate_mr_signal(df)
    if signal_type == "momentum":
        return generate_mom_signal(df)
    raise ValueError(f"Unknown signal type: {signal_type}")


def run_strategy(
    strategy_config: dict, data: Dict[str, pd.DataFrame]
) -> Dict[str, pd.Series]:
    """Run a strategy for each ticker based on configuration.

    Parameters
    ----------
    strategy_config : dict
        Dict containing keys:
        - "signals": list[str] of signal identifiers ("momentum", "mean_reversion")
        - "allowed_regimes": Optional list[str] of regimes to keep (default calm+normal)
    data : dict[str, pd.DataFrame]
        Mapping of ticker -> price DataFrame (must contain "Close")

    Returns
    -------
    dict[str, pd.Series]
        Mapping of ticker -> signal Series aligned to the DataFrame index.
    """

    # Cross-sectional strategy path
    if strategy_config.get("cross_sectional", False):
        n = int(strategy_config.get("top_n", 5))
        if n <= 0:
            raise ValueError("top_n must be positive for cross-sectional strategy")

        if strategy_config["signals"] == ["momentum"]:
            metric_df = compute_return_matrix(data, window=60)
            selection = rank_top_n_df(metric_df, n, highest=True)
        elif strategy_config["signals"] == ["mean_reversion"]:
            metric_df = compute_return_matrix(data, window=5)
            selection = rank_top_n_df(metric_df, n, highest=False)
        else:
            raise ValueError(
                "Cross-sectional strategy must specify exactly one "
                "signal type (momentum or mean_reversion)"
            )

        allowed_regimes = tuple(
            strategy_config.get("allowed_regimes", ("calm", "normal"))
        )
        signals_cs: Dict[str, pd.Series] = {
            col: apply_regime_filter(
                pd.Series(selection[col].astype(int)), allowed=allowed_regimes
            )
            for col in selection.columns
        }

        # Apply cash buffer logic if enabled
        if strategy_config.get("cash_buffer", False):
            ok_series = universe_momentum_ok(metric_df)
            for ticker in signals_cs:
                # Zero out signals when universe momentum is negative
                signals_cs[ticker] = signals_cs[ticker].where(ok_series, 0)

        # For long-only strategies, filter out negative signals
        if not strategy_config.get("long_short", False):
            for ticker in signals_cs:
                signals_cs[ticker] = signals_cs[ticker].where(
                    signals_cs[ticker] >= 0, 0
                )

        return signals_cs

    # ---- single‐stock (non cross-sectional) logic below ----

    signal_names: List[str] = strategy_config.get("signals", [])
    if not signal_names:
        raise ValueError("strategy_config must include non-empty 'signals' list")

    allowed_regimes = tuple(strategy_config.get("allowed_regimes", ("calm", "normal")))

    results: Dict[str, pd.Series] = {}

    for ticker, df in data.items():
        # Generate individual signals requested
        sig_components = [_gen_signal_by_type(name, df) for name in signal_names]

        if len(sig_components) == 1:
            combined = sig_components[0]
        else:
            # If multiple signals, simple ensemble logic: require alignment sign-wise
            combined = sig_components[0].copy()
            for s in sig_components[1:]:
                combined[(combined > 0) & (s <= 0)] = 0  # long only if all agree long
                combined[(combined < 0) & (s >= 0)] = 0  # short only if all agree short

        # Apply regime filter
        combined = apply_regime_filter(combined, allowed=allowed_regimes)

        # For long-only strategies, filter out negative signals
        if not strategy_config.get("long_short", False):
            combined = combined.where(combined >= 0, 0)

        results[ticker] = combined

    return results


# ---------------------------------------------------------------------------
# Simple ATR-based sizing & trailing-stop back-tester (long-only)
# ---------------------------------------------------------------------------


def backtest_with_atr(
    strategy_conf: dict,
    data: Dict[str, pd.DataFrame],
    start_equity: float = 1_000_000,
    *,
    risk_pct: float = 0.003,
    atr_window: int = 14,
    stop_mult: float = 2.0,
) -> pd.Series:
    """Back-test that sizes positions via ATR risk and applies a 2×ATR stop.

    Parameters
    ----------
    strategy_conf : dict
        Must contain key ``"signals_dict"`` mapping ticker → Series
        (1 = long, 0 = flat) produced by the signal engine.
    data : dict[str, pd.DataFrame]
        Historical OHLCV data (must include High, Low, Close).
    start_equity : float, default 1,000,000
        Starting capital in dollars.
    risk_pct : float, default 0.003
        Risk percentage per day.
    atr_window : int, default 14
        ATR window for calculating ATR.
    stop_mult : float, default 2.0
        Multiplier for ATR to determine stop loss.

    Returns
    -------
    pd.Series
        Daily equity curve.
    """

    if "signals_dict" not in strategy_conf:
        raise KeyError("strategy_conf must include 'signals_dict' for ATR back-test")

    signals_dict: Dict[str, pd.Series] = strategy_conf["signals_dict"]

    # Align all tickers to common date index (use first ticker as anchor)
    dates = next(iter(data.values())).index

    # Pre-compute ATR for each ticker
    atr_map: Dict[str, pd.Series] = {
        t: calc_atr(df, window=atr_window) for t, df in data.items()
    }

    equity = pd.Series(start_equity, index=dates, dtype=float)
    cash = start_equity

    positions: Dict[str, int] = {t: 0 for t in data.keys()}
    entry_price: Dict[str, float] = {t: np.nan for t in data.keys()}

    for i in range(1, len(dates)):
        today, prev_day = dates[i], dates[i - 1]

        # ------------------------------------------------------------------
        # 1) Check trailing-stop exits
        # ------------------------------------------------------------------
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
                # EXIT (close position)
                cash += qty * price_today  # Add position value back to cash
                positions[t] = 0
                entry_price[t] = float("nan")

        # ------------------------------------------------------------------
        # 2) Entries from signals (end of previous day)
        # ------------------------------------------------------------------
        for t, sig in signals_dict.items():
            if positions[t] != 0:
                continue  # already in position

            # Use safe lookup to avoid KeyError
            sig_prev = sig.get(prev_day, 0)
            if sig_prev is not None and sig_prev != 0:
                atr_prev_val = atr_map[t].get(prev_day)
                if atr_prev_val is None or pd.isna(atr_prev_val):
                    continue
                atr_prev = float(atr_prev_val)

                # Apply VIX-based risk throttling
                adj_risk = throttle_risk_pct(risk_pct, prev_day)
                base_qty = position_size(
                    equity.loc[prev_day], atr_prev, risk_pct=adj_risk
                )
                qty = int(
                    base_qty * sig_prev
                )  # +base_qty for long, -base_qty for short

                price_prev = data[t]["Close"].loc[prev_day]
                cost = abs(qty) * price_prev
                if cost <= cash or qty < 0:  # allow proceeds to fund shorts
                    if qty < 0:  # SHORT ENTRY
                        cash += cost  # receive cash
                    else:  # LONG ENTRY
                        cash -= cost  # pay cash
                    positions[t] = qty
                    entry_price[t] = price_prev

        # ------------------------------------------------------------------
        # 3) Mark-to-market portfolio equity
        # ------------------------------------------------------------------
        portfolio_val = cash + sum(
            positions[t] * data[t]["Close"].loc[today]
            for t in positions
            if positions[t] != 0  # Include both positive and negative positions
        )

        equity.iloc[i] = portfolio_val

    return equity
