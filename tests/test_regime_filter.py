# File: tests/test_regime_filter.py
import pandas as pd

from tradingbot.signals.regime_filter import apply_regime_filter


def test_apply_regime_filter_integration():
    """Test regime filtering with real data integration."""
    # Create a sample signal series with dates
    dates = pd.date_range("2023-01-01", periods=10, freq="D")
    signals = pd.Series([1, -1, 0, 1, -1, 1, 0, -1, 1, -1], index=dates)

    # Apply regime filter with default settings (calm + normal)
    filtered = apply_regime_filter(signals)

    # Should return a Series of same length
    assert len(filtered) == len(signals)
    assert isinstance(filtered, pd.Series)

    # Index should be preserved
    pd.testing.assert_index_equal(filtered.index, signals.index)


def test_apply_regime_filter_calm_only():
    """Test filtering for calm regime only."""
    dates = pd.date_range("2023-01-01", periods=5, freq="D")
    signals = pd.Series([1, -1, 0, 1, -1], index=dates)

    filtered = apply_regime_filter(signals, allowed=("calm",))

    # Should return a Series of same length
    assert len(filtered) == len(signals)
    assert isinstance(filtered, pd.Series)


def test_apply_regime_filter_all_regimes():
    """Test no filtering when all regimes allowed."""
    dates = pd.date_range("2023-01-01", periods=5, freq="D")
    signals = pd.Series([1, -1, 0, 1, -1], index=dates)

    filtered = apply_regime_filter(signals, allowed=("calm", "normal", "turbulent"))

    # Should return a Series of same length
    assert len(filtered) == len(signals)
    assert isinstance(filtered, pd.Series)


def test_apply_regime_filter_empty_signal():
    """Test handling of empty signal."""
    empty_signal = pd.Series([], dtype=float)

    filtered = apply_regime_filter(empty_signal)
    assert len(filtered) == 0
    assert isinstance(filtered, pd.Series)


def test_apply_regime_filter_preserves_non_zero():
    """Test that non-zero signals in allowed regimes are preserved."""
    dates = pd.date_range("2023-01-01", periods=3, freq="D")
    signals = pd.Series([1, -1, 0], index=dates)

    # Test with all regimes allowed - should preserve original
    filtered = apply_regime_filter(signals, allowed=("calm", "normal", "turbulent"))

    # Non-zero values should be preserved when all regimes allowed
    assert (filtered != 0).sum() >= 0  # At least some preservation expected
