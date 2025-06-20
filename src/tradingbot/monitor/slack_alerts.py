# File: src/tradingbot/monitor/slack_alerts.py
from pathlib import Path
from typing import Tuple

import yaml
from slack_sdk import WebClient

CFG = Path("config/slack.yaml")


def load_slack_client() -> Tuple[WebClient, str]:
    if not CFG.exists():
        raise FileNotFoundError(
            "Copy slack_example.yaml → slack.yaml and fill token/channel."
        )
    cfg = yaml.safe_load(CFG.read_text())["slack"]
    return WebClient(token=cfg["token"]), cfg["channel"]


def send_slack_message(text: str):
    client, channel = load_slack_client()
    client.chat_postMessage(channel=channel, text=text)
