from __future__ import annotations

from typing import Dict, List

import pandas as pd

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
        results[ticker] = combined

    return results
