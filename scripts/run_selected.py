#!/usr/bin/env python

import argparse
from typing import cast

import pandas as pd

from tradingbot.backtest.metrics import backtest_metrics
from tradingbot.backtest.save_params import load_saved_params
from tradingbot.data.universe import get_universe
from tradingbot.data.yfinance_downloader import download_stock_data
from tradingbot.signals.mean_reversion import generate_mr_signal
from tradingbot.signals.momentum import generate_mom_signal


def run_config(cfg: dict, symbol: str):
    df = download_stock_data(symbol, start="2023-01-03")
    sig_mr = generate_mr_signal(
        df, enter_thresh=cfg["enter_thresh"], window=cfg["window"]
    )
    sig_mom = generate_mom_signal(
        df,
        long_thresh=cfg["long_thresh"],
        short_thresh=cfg["short_thresh"],
        window=cfg["window"],
    )
    combined = ((sig_mr + sig_mom) / 2).round().clip(-1, 1)
    close_series = cast(pd.Series, df["Close"])
    return backtest_metrics(close_series, combined)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--symbols",
        nargs="+",
        default=None,
        help="Ticker list; default universe if omitted",
    )
    args = parser.parse_args()

    universe = get_universe(args.symbols)
    best_cfgs = load_saved_params()

    for cfg in best_cfgs:
        print(f"\nRunning config: {cfg}")
        for sym in universe:
            stats = run_config(cfg, sym)
            print(f"{sym}: {stats}")


if __name__ == "__main__":
    main()
