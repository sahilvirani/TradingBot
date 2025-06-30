import subprocess, sys, pathlib, json, os

def test_cli_runs_quickly():
    cmd = [
        sys.executable, "scripts/full_backtest.py",
        "--start","2021-01-04","--end","2021-02-01",
        "--capital","50000","--risk_pct","0.001","--top_n","10",
    ]
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=40)
    assert out.returncode == 0
    assert "Performance vs SPY" in out.stdout
    tag = "2021-01-04_2021-02-01"
    assert pathlib.Path(f"out/trade_log_{tag}.csv").exists() 