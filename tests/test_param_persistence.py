# File: tests/test_param_persistence.py

from tradingbot.backtest.aggregate import aggregate_metrics
from tradingbot.backtest.batch_runner import grid_search_batch
from tradingbot.backtest.save_params import load_saved_params, save_top_params


def test_save_and_load_params(tmp_path, monkeypatch):
    # use tmp config path to avoid clobbering main config
    monkeypatch.setattr(
        "tradingbot.backtest.save_params.CONFIG_PATH", tmp_path / "test_params.yaml"
    )

    df = grid_search_batch(start="2023-01-03", universe=["AAPL"])
    agg = aggregate_metrics(df)
    save_top_params(agg, top_n=2)
    loaded = load_saved_params()
    assert len(loaded) == 2
    assert "enter_thresh" in loaded[0]
