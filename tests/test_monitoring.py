# File: tests/test_monitoring.py
import threading
import time


def test_prometheus_export(monkeypatch):
    # Import first
    from tradingbot.monitor.heartbeat import update_metrics
    from tradingbot.monitor.prom import start_prom_server

    # Monkey-patch the Slack client loader to avoid config file requirement
    def mock_slack_client():
        class MockClient:
            def chat_postMessage(self, channel, text):
                print(f"MOCK SLACK to {channel}: {text}")

        return MockClient(), "#test-channel"

    monkeypatch.setattr(
        "tradingbot.monitor.slack_alerts.load_slack_client", mock_slack_client
    )

    # Start exporter on free port in background
    threading.Thread(
        target=start_prom_server, kwargs={"port": 9000}, daemon=True
    ).start()
    time.sleep(0.5)

    # Push a big draw-down => should call mocked Slack (no exception)
    update_metrics(pnl_pct=-2.0, dd_pct=-6.0, open_pos=3)

    # Test that metrics were set (basic validation)
    from tradingbot.monitor.prom import drawdown_gauge, open_pos_gauge, pnl_gauge

    assert pnl_gauge._value._value == -2.0
    assert drawdown_gauge._value._value == -6.0
    assert open_pos_gauge._value._value == 3
