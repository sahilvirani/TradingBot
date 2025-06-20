# File: tests/test_is_oos_eval.py
import tempfile
from pathlib import Path

import pytest
import yaml

from tradingbot.backtest.is_oos_eval import run_is_oos_test


@pytest.fixture
def temp_params_file(monkeypatch):
    """Create a temporary parameters file for testing."""
    # Create test parameters
    test_params = [
        {"enter_thresh": -1.0, "long_thresh": 0.05, "short_thresh": -0.05, "window": 20}
    ]

    # Create temporary file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(test_params, f)
        temp_path = Path(f.name)

    # Mock the parameters file path
    monkeypatch.setattr("tradingbot.backtest.save_params.CONFIG_PATH", temp_path)

    yield temp_path

    # Cleanup
    temp_path.unlink(missing_ok=True)


def test_is_oos_eval_small(temp_params_file):
    """Test IS/OOS evaluation with minimal data."""
    res = run_is_oos_test(symbols=["AAPL", "MSFT"], oos_end="2025-02-01")

    # Ensure we got results
    assert not res.empty
    assert "OOS_Sharpe" in res.columns
    assert "IS_Sharpe" in res.columns
    assert len(res) >= 2  # At least one result per symbol
