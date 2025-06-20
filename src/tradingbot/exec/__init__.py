# File: src/tradingbot/exec/__init__.py

# Execution module

try:
    from .alpaca_client import AlpacaClient  # noqa: F401
    from .creds import load_creds  # noqa: F401
    from .order_router import DailySignalExecutor  # noqa: F401

    _EXEC_AVAILABLE = True
    __all__ = ["AlpacaClient", "load_creds", "DailySignalExecutor"]
except ImportError:
    AlpacaClient = None
    load_creds = None
    DailySignalExecutor = None
    _EXEC_AVAILABLE = False
    __all__ = []
