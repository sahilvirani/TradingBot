# File: src/tradingbot/risk/monte_carlo.py

import numpy as np
import pandas as pd


def monte_carlo_paths(returns: pd.Series, n_paths: int = 1000) -> pd.DataFrame:
    """
    Boot-strap daily returns to create many equity-curve paths.
    """
    ret = np.array(returns.dropna().values)
    paths = np.random.choice(ret, size=(n_paths, len(ret)), replace=True)
    equity = (1 + paths).cumprod(axis=1)
    return pd.DataFrame(equity, index=range(n_paths), columns=returns.index)


def mc_var_es(equity_paths: pd.DataFrame, level: float = 0.05) -> dict[str, float]:
    """
    Compute VaR and expected shortfall on terminal P/L.
    """
    final = equity_paths.iloc[:, -1] - 1  # pct return
    var = final.quantile(level)
    es = final[final <= var].mean()
    return {"VaR": var, "ES": es}
