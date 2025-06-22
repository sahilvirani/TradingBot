--

**User**

ok now follow the prompts for sprint 19: 🚀 Sprint 19 — Automated Success-Criteria Report
Objective
Generate a single, repeatable report that answers:

How many strategy configs traded?

Which configs hit all targets

Sharpe ≥ 0 .7

Max-DD ≤ 15 %

Positive excess return vs SPY in both 2020-crash and 2022 bear year

Portfolio-level summary (CAGR, Sharpe, Max-DD)

CSV + pretty console table for quick review

You already have:

benchmark_compare.py — returns Sharpe / Max-DD / excess-period flag.

Universe lists & overlayed equity curves from the last mini-sprint.

We’ll wire those pieces into a single report generator, add a tiny unit-test, and a helper CLI script.
This uses only free Python libs (pandas, tabulate).

① Install tiny helper lib (one-off)
bash
Copy
Edit
poetry add tabulate
🤖 Cursor-ready prompts
(paste each prompt in order)

🧩 Prompt 1 – success_report.py
python
Copy
Edit

# File: src/tradingbot/evaluation/success_report.py

from **future** import annotations
import pandas as pd
from pathlib import Path
from tabulate import tabulate

from tradingbot.config import strategies # your YAML loader
from tradingbot.evaluation.benchmark_compare import benchmark_comparison
from tradingbot.data.sp500_top50 import get_top50_symbols

UNIVERSE = get_top50_symbols()
OUT_PATH = Path("reports/success_report.csv")
TARGETS = {"sharpe": 0.70, "max_dd": -0.15, "excess_periods": 2}

def evaluate_all() -> pd.DataFrame:
rows = []
for cfg in strategies:
name = cfg["name"]
print(f"Running {name} …")
metrics = benchmark_comparison(cfg, UNIVERSE, return_dict=True) # benchmark_comparison must now return dict: # {'sharpe': float, 'max_dd': float, 'excess_periods': int, 'trades': int}
row = {"name": name, \*\*metrics}
row["meets_all"] = (
metrics["sharpe"] >= TARGETS["sharpe"] and
metrics["max_dd"] >= TARGETS["max_dd"] and
metrics["excess_periods"] >= TARGETS["excess_periods"]
)
rows.append(row)
df = pd.DataFrame(rows)
OUT_PATH.parent.mkdir(exist_ok=True, parents=True)
df.to_csv(OUT_PATH, index=False)
return df

def print_summary(df: pd.DataFrame):
active = (df["trades"] > 0).sum()
total = len(df)
print(f"\nActive configs: {active}/{total} ({active/total\*100:.1f}%)")
winners = df[df["meets_all"]]
print(f"Configs meeting ALL targets: {len(winners)}")
cols = ["name", "sharpe", "max_dd", "excess_periods", "trades"]
print(tabulate(df[cols], headers="keys", floatfmt=".2f"))

if **name** == "**main**":
summary = evaluate_all()
print_summary(summary)
🧩 Prompt 2 – make benchmark_comparison return a dict
Add return at the bottom of src/tradingbot/evaluation/benchmark_compare.py:

python
Copy
Edit # existing prints …
return {
"sharpe": strat_sharpe,
"max_dd": strat_maxdd,
"excess_periods": sum(
1 for v in excess_list if v > 0 # you'll need to append excess values to a list
),
"trades": int((daily_ret != 0).sum())
}
(If you named variables differently, adapt accordingly. Also create excess_list inside the loop from Sprint 18.)

🧩 Prompt 3 – unit-test quick pass/fail
python
Copy
Edit

# File: tests/test_success_report.py

from tradingbot.evaluation.success_report import evaluate_all, TARGETS

def test_success_report_runs():
df = evaluate_all() # At least one strategy should trade
assert (df["trades"] > 0).any() # Verify dataframe has required columns
for col in ["sharpe","max_dd","excess_periods"]:
assert col in df.columns # Ensure Sharpe values are finite
assert df["sharpe"].replace([float("inf"), float("-inf")], pd.NA).dropna().size > 0
🧩 Prompt 4 – helper CLI script
bash
Copy
Edit

# File: scripts/run_success_report.sh

#!/usr/bin/env bash
poetry run python -m tradingbot.evaluation.success_report
chmod +x scripts/run_success_report.sh

✅ After prompts
Run tests & report

bash
Copy
Edit
pytest tests/test_success_report.py
./scripts/run_success_report.sh
Example console:

yaml
Copy
Edit
Active configs: 4/4 (100.0%)
Configs meeting ALL targets: 3
name sharpe max_dd excess_periods trades

---

MomentumTop5 0.93 -0.13 2 760
MeanReversionTop5 0.84 -0.14 2 812
MomentumOnly 0.75 -0.12 2 1450
MeanReversionOnly 0.42 -0.18 1 600
Commit & push

Before you commit/push any files show me the numeric results

---

**Cursor**

```python
// ... existing code ...
@@
-    # Metrics
+    # Metrics
@@
-    # Print headline metrics
+# Print headline metrics
@@
-    turbulent_periods = [
+    turbulent_periods = [
@@
-    for start, end in turbulent_periods:
+    excess_list = []
+    for start, end in turbulent_periods:
@@
-        excess = strat_ret_period - spy_ret_period
+        excess = strat_ret_period - spy_ret_period
+        excess_list.append(excess)
@@
-        )
+        )
+
+    # Return dictionary if requested
+    if strategy_conf.get("_return_dict", False):
+        return {
+            "sharpe": float(strat_sharpe),
+            "max_dd": float(strat_maxdd),
+            "excess_periods": int(sum(1 for v in excess_list if v > 0)),
+            "trades": int((daily_ret != 0).sum()),
+        }
+
+    # also support external param
+    return None

```

```python
from __future__ import annotations

from pathlib import Path

import pandas as pd
from tabulate import tabulate

from tradingbot.config import strategies
from tradingbot.evaluation.benchmark_compare import benchmark_comparison

# Fallback universe helper
try:
    from tradingbot.data.sp500_top50 import get_top50_symbols  # type: ignore

    UNIVERSE = get_top50_symbols()
except ImportError:
    from tradingbot.data.universe import get_universe

    # If top-50 helper missing, fall back to cached CSV list or default 5-stock list.
    UNIVERSE = get_universe()

OUT_PATH = Path("reports/success_report.csv")
TARGETS = {"sharpe": 0.70, "max_dd": -0.15, "excess_periods": 2}


def evaluate_all() -> pd.DataFrame:
    rows: list[dict] = []
    for cfg in strategies:
        name = cfg.get("name", "<unnamed>")
        print(f"Running {name} …")
        cfg_local = dict(cfg)  # shallow copy so we can inject flag
        cfg_local["_return_dict"] = True
        metrics = benchmark_comparison(cfg_local, UNIVERSE)
        if metrics is None:
            # fallback in case function returns None
            continue
        row = {"name": name, **metrics}
        row["meets_all"] = (
            metrics["sharpe"] >= TARGETS["sharpe"]
            and metrics["max_dd"] >= TARGETS["max_dd"]
            and metrics["excess_periods"] >= TARGETS["excess_periods"]
        )
        rows.append(row)

    df = pd.DataFrame(rows)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_PATH, index=False)
    return df


def print_summary(df: pd.DataFrame):
    active = int((df["trades"] > 0).sum())
    total = len(df)
    print(f"\nActive configs: {active}/{total}  ({active/total*100:.1f}%)")
    winners = df[df["meets_all"]]
    print(f"Configs meeting ALL targets: {len(winners)}")
    cols = ["name", "sharpe", "max_dd", "excess_periods", "trades", "meets_all"]
    print(tabulate(df[cols], headers="keys", floatfmt=".2f"))


if __name__ == "__main__":
    _df = evaluate_all()
    print_summary(_df)

```

```python
import pandas as pd
from tradingbot.evaluation.success_report import evaluate_all, TARGETS

def test_success_report_runs():
    df = evaluate_all()
    assert (df["trades"] > 0).any()
    for col in ["sharpe", "max_dd", "excess_periods"]:
        assert col in df.columns
    finite = df["sharpe"].replace([float("inf"), float("-inf")], pd.NA).dropna()
    assert finite.size > 0

```

Sprint-19 report run complete:

Active configs: 4/4 (100 %)  
Configs meeting ALL targets: 0 (no strategy hit every criterion with the current overlay and 5-stock universe).

┌───────────────────┬────────┬────────┬────────────────┬────────┐
│ name │ Sharpe │ Max-DD │ excess_periods │ trades │
├───────────────────┼────────┼────────┼────────────────┼────────┤
│ MeanReversionOnly │ 0.03 │ −22 % │ 1 │ 305 │
│ MomentumOnly │ 1.21 │ −26 % │ 1 │ 949 │
│ MomentumTop5 │ 1.05 │ −31 % │ 1 │ 1347 │
│ MeanReversionTop5 │ 0.83 │ −26 % │ 1 │ 775 │
└───────────────────┴────────┴────────┴────────────────┴────────┘

(Sharpe ≥ 0.70 met by 3 strategies, but Max-DD ≤ 15 % or positive SPY-excess in both stress periods not yet achieved, hence 0 full-winners.)

Let me know if you’d like adjustments (e.g., lower risk_pct, wider universes) before we commit this reporting module.
