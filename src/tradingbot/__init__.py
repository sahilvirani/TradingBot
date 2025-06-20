# Trading Bot Package

# Sprint 9: Multi-ticker batch backtesting
from tradingbot.backtest.aggregate import aggregate_metrics
from tradingbot.backtest.batch_runner import grid_search_batch

# Sprint 10: Parameter persistence
from tradingbot.backtest.save_params import load_saved_params, save_top_params
from tradingbot.data.universe import DEFAULT_UNIVERSE, get_universe

# Sprint 11: Execution sandbox (optional dependencies)
try:
    from tradingbot.exec.alpaca_client import AlpacaClient
    from tradingbot.exec.order_router import DailySignalExecutor

    _EXEC_AVAILABLE = True
except ImportError:
    AlpacaClient = None
    DailySignalExecutor = None
    _EXEC_AVAILABLE = False

__all__ = [
    "DEFAULT_UNIVERSE",
    "get_universe",
    "grid_search_batch",
    "aggregate_metrics",
    "save_top_params",
    "load_saved_params",
]

# Add execution classes only if available
if _EXEC_AVAILABLE:
    __all__.extend(["DailySignalExecutor", "AlpacaClient"])
