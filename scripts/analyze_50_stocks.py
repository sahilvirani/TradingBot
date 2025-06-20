#!/usr/bin/env python3
"""
Comprehensive Analysis of 50-Stock Evaluation Results
Generates detailed visualizations and statistics.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
import seaborn as sns

# Set style for better looking plots
plt.style.use("seaborn-v0_8")
sns.set_palette("husl")


def load_results():
    """Load the evaluation results."""
    results_path = Path("data/is_oos_results.csv")
    if not results_path.exists():
        raise FileNotFoundError(f"Results file not found: {results_path}")

    df = pd.read_csv(results_path)

    # Convert percentage columns to decimal
    df["OOS_Return"] = df["OOS_Return[%]"] / 100
    df["IS_Return"] = df["IS_Return[%]"] / 100
    df["OOS_MaxDD"] = df["OOS_MaxDD[%]"] / 100
    df["IS_MaxDD"] = df["IS_MaxDD[%]"] / 100
    df["OOS_Trades"] = df["OOS_Trades"]
    df["IS_Trades"] = df["IS_Trades"]

    print(f"📊 Loaded {len(df)} results for {df['Symbol'].nunique()} stocks")
    return df


def summary_stats(df):
    """Generate summary statistics."""
    print("\n" + "=" * 60)
    print("📈 COMPREHENSIVE 50-STOCK EVALUATION SUMMARY")
    print("=" * 60)

    # Basic stats
    print(f"Total Evaluations: {len(df)}")
    print(f"Unique Stocks: {df['Symbol'].nunique()}")
    print(f"Parameter Sets per Stock: {len(df) // df['Symbol'].nunique()}")

    # Performance metrics
    print("\n🎯 OUT-OF-SAMPLE PERFORMANCE:")
    print(f"Mean OOS Return: {df['OOS_Return'].mean():.2%}")
    print(f"Median OOS Return: {df['OOS_Return'].median():.2%}")
    best_idx = df["OOS_Return"].idxmax()
    worst_idx = df["OOS_Return"].idxmin()
    print(
        f"Best OOS Return: {df['OOS_Return'].max():.2%} "
        f"({df.loc[best_idx, 'Symbol']})"
    )
    print(
        f"Worst OOS Return: {df['OOS_Return'].min():.2%} "
        f"({df.loc[worst_idx, 'Symbol']})"
    )

    # Sharpe ratios
    finite_sharpe = df["OOS_Sharpe"][np.isfinite(df["OOS_Sharpe"])]
    print("\n📊 SHARPE RATIOS (finite values only):")
    if len(finite_sharpe) > 0:
        print(f"Mean OOS Sharpe: {finite_sharpe.mean():.2f}")
        print(f"Median OOS Sharpe: {finite_sharpe.median():.2f}")
        print(f"Best OOS Sharpe: {finite_sharpe.max():.2f}")
    else:
        print("No finite Sharpe ratios found")

    # Trade activity
    print("\n💹 TRADING ACTIVITY:")
    print(f"Mean OOS Trades: {df['OOS_Trades'].mean():.1f}")
    print(f"Median OOS Trades: {df['OOS_Trades'].median():.1f}")
    print(f"Max OOS Trades: {df['OOS_Trades'].max()}")
    zero_trades = (df["OOS_Trades"] == 0).sum()
    zero_pct = (df["OOS_Trades"] == 0).mean()
    print(f"Strategies with 0 trades: {zero_trades} ({zero_pct:.1%})")

    # Top performers
    print("\n🏆 TOP 10 PERFORMERS (OOS Return):")
    top10 = df.nlargest(10, "OOS_Return")[
        ["Symbol", "OOS_Return", "OOS_Sharpe", "OOS_Trades"]
    ]
    for _, row in top10.iterrows():
        sharpe_str = (
            f"{row['OOS_Sharpe']:.2f}" if np.isfinite(row["OOS_Sharpe"]) else "inf"
        )
        print(
            f"  {row['Symbol']:6} | {row['OOS_Return']:8.2%} | "
            f"Sharpe: {sharpe_str:>6} | Trades: {row['OOS_Trades']:3.0f}"
        )


def create_visualizations(df):
    """Create comprehensive visualizations."""

    # Create figure with subplots
    plt.figure(figsize=(20, 15))

    # 1. OOS Return Distribution
    plt.subplot(3, 3, 1)
    plt.hist(df["OOS_Return"], bins=30, alpha=0.7, edgecolor="black")
    plt.axvline(
        df["OOS_Return"].mean(),
        color="red",
        linestyle="--",
        label=f'Mean: {df["OOS_Return"].mean():.2%}',
    )
    plt.axvline(
        df["OOS_Return"].median(),
        color="orange",
        linestyle="--",
        label=f'Median: {df["OOS_Return"].median():.2%}',
    )
    plt.xlabel("Out-of-Sample Return")
    plt.ylabel("Frequency")
    plt.title("Distribution of OOS Returns")
    plt.legend()
    plt.gca().xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{x:.0%}"))

    # 2. Top 15 Performers
    plt.subplot(3, 3, 2)
    top15 = df.nlargest(15, "OOS_Return")
    bars = plt.barh(range(len(top15)), top15["OOS_Return"])
    plt.yticks(range(len(top15)), top15["Symbol"])
    plt.xlabel("Out-of-Sample Return")
    plt.title("Top 15 Performers (OOS Return)")
    plt.gca().xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{x:.0%}"))

    # Color bars based on performance
    for i, bar in enumerate(bars):
        if top15.iloc[i]["OOS_Return"] > 0.01:  # >1%
            bar.set_color("darkgreen")
        elif top15.iloc[i]["OOS_Return"] > 0.005:  # >0.5%
            bar.set_color("green")
        elif top15.iloc[i]["OOS_Return"] > 0:
            bar.set_color("lightgreen")
        else:
            bar.set_color("lightcoral")

    # 3. IS vs OOS Return Scatter
    plt.subplot(3, 3, 3)
    plt.scatter(df["IS_Return"], df["OOS_Return"], alpha=0.6)
    plt.xlabel("In-Sample Return")
    plt.ylabel("Out-of-Sample Return")
    plt.title("IS vs OOS Returns")

    # Add diagonal line for reference
    min_val = min(df["IS_Return"].min(), df["OOS_Return"].min())
    max_val = max(df["IS_Return"].max(), df["OOS_Return"].max())
    plt.plot(
        [min_val, max_val],
        [min_val, max_val],
        "r--",
        alpha=0.5,
        label="Perfect Correlation",
    )
    plt.legend()
    plt.gca().xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{x:.0%}"))
    plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{x:.0%}"))

    # 4. Trading Activity Distribution
    plt.subplot(3, 3, 4)
    plt.hist(df["OOS_Trades"], bins=20, alpha=0.7, edgecolor="black")
    plt.xlabel("Number of OOS Trades")
    plt.ylabel("Frequency")
    plt.title("Trading Activity Distribution")
    plt.axvline(
        df["OOS_Trades"].mean(),
        color="red",
        linestyle="--",
        label=f'Mean: {df["OOS_Trades"].mean():.1f}',
    )
    plt.legend()

    # 5. Sharpe Ratio Distribution (finite values only)
    plt.subplot(3, 3, 5)
    finite_sharpe = df["OOS_Sharpe"][np.isfinite(df["OOS_Sharpe"])]
    if len(finite_sharpe) > 0:
        plt.hist(finite_sharpe, bins=20, alpha=0.7, edgecolor="black")
        plt.axvline(
            finite_sharpe.mean(),
            color="red",
            linestyle="--",
            label=f"Mean: {finite_sharpe.mean():.2f}",
        )
        plt.xlabel("OOS Sharpe Ratio")
        plt.ylabel("Frequency")
        plt.title(f"Sharpe Ratio Distribution\n({len(finite_sharpe)} finite values)")
        plt.legend()
    else:
        plt.text(
            0.5,
            0.5,
            "No finite Sharpe ratios",
            ha="center",
            va="center",
            transform=plt.gca().transAxes,
        )
        plt.title("Sharpe Ratio Distribution")

    # 6. Return by Stock (average across parameter sets)
    plt.subplot(3, 3, 6)
    stock_avg = df.groupby("Symbol")["OOS_Return"].mean().sort_values(ascending=False)
    top_stocks = stock_avg.head(15)
    bars = plt.barh(range(len(top_stocks)), top_stocks.values)
    plt.yticks(range(len(top_stocks)), top_stocks.index)
    plt.xlabel("Average OOS Return")
    plt.title("Top 15 Stocks (Avg Return)")
    plt.gca().xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{x:.0%}"))

    # Color bars
    for i, bar in enumerate(bars):
        if top_stocks.iloc[i] > 0.005:  # >0.5%
            bar.set_color("darkgreen")
        elif top_stocks.iloc[i] > 0.001:  # >0.1%
            bar.set_color("green")
        elif top_stocks.iloc[i] >= 0:
            bar.set_color("lightgreen")
        else:
            bar.set_color("lightcoral")

    # 7. Max Drawdown Distribution
    plt.subplot(3, 3, 7)
    plt.hist(df["OOS_MaxDD"], bins=20, alpha=0.7, edgecolor="black")
    plt.xlabel("Max Drawdown")
    plt.ylabel("Frequency")
    plt.title("Max Drawdown Distribution")
    plt.axvline(
        df["OOS_MaxDD"].mean(),
        color="red",
        linestyle="--",
        label=f'Mean: {df["OOS_MaxDD"].mean():.2%}',
    )
    plt.legend()
    plt.gca().xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{x:.0%}"))

    # 8. Parameter Analysis - Window Size Impact
    plt.subplot(3, 3, 8)
    window_perf = df.groupby("window")["OOS_Return"].agg(["mean", "std"]).reset_index()
    plt.errorbar(
        window_perf["window"],
        window_perf["mean"],
        yerr=window_perf["std"],
        marker="o",
        capsize=5,
        capthick=2,
    )
    plt.xlabel("Window Size")
    plt.ylabel("Average OOS Return")
    plt.title("Performance by Window Size")
    plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{x:.1%}"))
    plt.grid(True, alpha=0.3)

    # 9. Risk-Return Scatter
    plt.subplot(3, 3, 9)
    # Filter out infinite Sharpe ratios for this plot
    finite_mask = np.isfinite(df["OOS_Sharpe"])
    if finite_mask.sum() > 0:
        plt.scatter(
            df.loc[finite_mask, "OOS_MaxDD"],
            df.loc[finite_mask, "OOS_Return"],
            c=df.loc[finite_mask, "OOS_Sharpe"],
            cmap="RdYlGn",
            alpha=0.6,
        )
        plt.colorbar(label="Sharpe Ratio")
        plt.xlabel("Max Drawdown")
        plt.ylabel("OOS Return")
        plt.title("Risk-Return Profile")
        plt.gca().xaxis.set_major_formatter(
            ticker.FuncFormatter(lambda x, p: f"{x:.0%}")
        )
        plt.gca().yaxis.set_major_formatter(
            ticker.FuncFormatter(lambda x, p: f"{x:.0%}")
        )
    else:
        plt.text(
            0.5,
            0.5,
            "No finite Sharpe ratios\nfor risk-return analysis",
            ha="center",
            va="center",
            transform=plt.gca().transAxes,
        )
        plt.title("Risk-Return Profile")

    plt.tight_layout()
    plt.savefig("data/50_stock_analysis.png", dpi=300, bbox_inches="tight")
    print("\n📊 Comprehensive visualization saved to: data/50_stock_analysis.png")
    plt.show()


def parameter_analysis(df):
    """Analyze parameter set performance."""
    print("\n" + "=" * 50)
    print("🔧 PARAMETER SET ANALYSIS")
    print("=" * 50)

    # Group by parameter combination
    param_cols = ["enter_thresh", "long_thresh", "short_thresh", "window"]
    param_groups = (
        df.groupby(param_cols)
        .agg(
            {
                "OOS_Return": ["mean", "std", "count"],
                "OOS_Trades": "mean",
                "OOS_Sharpe": lambda x: (
                    np.mean(x[np.isfinite(x)]) if np.any(np.isfinite(x)) else np.nan
                ),
            }
        )
        .round(4)
    )

    param_groups.columns = ["_".join(col).strip() for col in param_groups.columns]
    param_groups = param_groups.sort_values("OOS_Return_mean", ascending=False)

    print("\nParameter Set Performance (sorted by mean OOS return):")
    print(param_groups.to_string())

    return param_groups


def sector_analysis(df):
    """Basic sector analysis based on stock symbols."""
    print("\n" + "=" * 50)
    print("🏭 SECTOR ANALYSIS (Simplified)")
    print("=" * 50)

    # Simple sector mapping based on known stocks
    sector_map = {
        "AAPL": "Technology",
        "MSFT": "Technology",
        "NVDA": "Technology",
        "GOOGL": "Technology",
        "META": "Technology",
        "ORCL": "Technology",
        "CRM": "Technology",
        "ADBE": "Technology",
        "AMD": "Technology",
        "INTC": "Technology",
        "QCOM": "Technology",
        "TXN": "Technology",
        "AMAT": "Technology",
        "AMZN": "Consumer Discretionary",
        "TSLA": "Consumer Discretionary",
        "HD": "Consumer Discretionary",
        "MCD": "Consumer Discretionary",
        "NKE": "Consumer Discretionary",
        "BKNG": "Consumer Discretionary",
        "ABNB": "Consumer Discretionary",
        "DIS": "Consumer Discretionary",
        "JPM": "Financials",
        "BAC": "Financials",
        "WFC": "Financials",
        "GS": "Financials",
        "V": "Financials",
        "MA": "Financials",
        "PYPL": "Financials",
        "SPGI": "Financials",
        "JNJ": "Healthcare",
        "LLY": "Healthcare",
        "UNH": "Healthcare",
        "MRK": "Healthcare",
        "ABBV": "Healthcare",
        "TMO": "Healthcare",
        "XOM": "Energy",
        "CVX": "Energy",
        "WMT": "Consumer Staples",
        "PG": "Consumer Staples",
        "COST": "Consumer Staples",
        "PEP": "Consumer Staples",
        "KO": "Consumer Staples",
        "BRK-B": "Financials",
        "AVGO": "Technology",
        "LIN": "Materials",
        "NFLX": "Communication Services",
        "CMCSA": "Communication Services",
        "RTX": "Industrials",
        "CAT": "Industrials",
        "IBM": "Technology",
    }

    df["Sector"] = df["Symbol"].map(sector_map).fillna("Other")

    sector_perf = (
        df.groupby("Sector")
        .agg({"OOS_Return": ["mean", "std", "count"], "OOS_Trades": "mean"})
        .round(4)
    )

    sector_perf.columns = ["_".join(col).strip() for col in sector_perf.columns]
    sector_perf = sector_perf.sort_values("OOS_Return_mean", ascending=False)

    print("\nSector Performance:")
    print(sector_perf.to_string())


def main():
    """Main analysis function."""
    print("🚀 Starting comprehensive 50-stock analysis...")

    # Load results
    df = load_results()

    # Generate summary statistics
    summary_stats(df)

    # Create visualizations
    create_visualizations(df)

    # Parameter analysis
    parameter_analysis(df)

    # Sector analysis
    sector_analysis(df)

    print(
        "\n✅ Analysis complete! Check data/50_stock_analysis.png for visualizations."
    )


if __name__ == "__main__":
    main()
