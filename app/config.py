import os
from dataclasses import dataclass


@dataclass
class Settings:
    openai_api_key: str
    openai_model: str
    discord_webhook_url: str
    max_sources_per_run: int
    request_timeout_seconds: int

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            openai_api_key=os.environ["OPENAI_API_KEY"],
            openai_model=os.environ.get("OPENAI_MODEL", "gpt-5"),
            discord_webhook_url=os.environ["DISCORD_WEBHOOK_URL"],
            max_sources_per_run=int(os.environ.get("MAX_SOURCES_PER_RUN", "1")),
            request_timeout_seconds=int(os.environ.get("REQUEST_TIMEOUT_SECONDS", "30")),
        )