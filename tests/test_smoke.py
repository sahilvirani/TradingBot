"""Smoke test to verify basic package functionality."""

import tradingbot


def test_package_imports():
    """Test that the tradingbot package can be imported successfully."""
    assert True


def test_package_exists():
    """Test that the tradingbot module exists and has expected attributes."""
    assert tradingbot is not None
    assert hasattr(tradingbot, "__file__") or hasattr(tradingbot, "__path__")
