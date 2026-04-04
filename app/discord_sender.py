from __future__ import annotations

import requests


class DiscordSendError(Exception):
    pass


def send_discord_message(webhook_url: str, content: str, timeout: int = 30) -> None:
    payload = {"content": content}
    response = requests.post(webhook_url, json=payload, timeout=timeout)
    if response.status_code >= 400:
        raise DiscordSendError(
            f"Discord webhook failed: {response.status_code} {response.text}"
        )


def send_long_message(
    webhook_url: str,
    content: str,
    timeout: int = 30,
    max_len: int = 1800,
) -> None:
    if len(content) <= max_len:
        send_discord_message(webhook_url, content, timeout=timeout)
        return

    start = 0
    while start < len(content):
        chunk = content[start : start + max_len]
        send_discord_message(webhook_url, chunk, timeout=timeout)
        start += max_len