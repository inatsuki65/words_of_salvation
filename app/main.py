from __future__ import annotations

import json
from pathlib import Path

from app.config import Settings
from app.get_news import update_sources_json
from app.discord_sender import send_long_message
from app.fetcher import FetchError, fetch_source
from app.llm_client import LLMClient
from app.pipeline import run_pipeline
from app.config import DATA_DIR
from app.config import SOURCES_PATH

# DATA_DIR = Path(__file__).resolve().parent.parent / "data"
# SOURCES_PATH = DATA_DIR / "sources.json"


def load_sources() -> list[dict]:
    with SOURCES_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    # ① Googleニュースから最新記事を取得して sources.json を更新
    update_sources_json()
    
    settings = Settings.from_env()
    llm = LLMClient(
        api_key=settings.openai_api_key,
        model=settings.openai_model,
    )

    sources = load_sources()[: settings.max_sources_per_run]

    for source in sources:
        name = source["name"]
        url = source["url"]
        source_type = source["type"]

        try:
            fetched = fetch_source(
                url=url,
                source_type=source_type,
                timeout=settings.request_timeout_seconds,
            )

            result = run_pipeline(llm, fetched)

            meta_message = build_meta_message(
                source_name=name,
                fetched_title=fetched.title,
                url=fetched.url,
                summary=result.summary,
                classification=result.classification,
                safety_review=result.safety_review,
            )

            send_long_message(settings.discord_webhook_url, meta_message)
            send_long_message(
                settings.discord_webhook_url,
                "```markdown\n" + result.blog_markdown + "\n```",
            )
            send_long_message(
                settings.discord_webhook_url,
                "```markdown\n" + result.personal_words + "\n```",
            )
            send_long_message(
                settings.discord_webhook_url,
                "```text\n" + result.image_prompt + "\n```",
            )

        except Exception as exc:
            error_message = (
                "## pipeline error\n"
                f"source: {name}\n"
                f"url: {url}\n"
                f"error: {type(exc).__name__}: {exc}"
            )
            send_long_message(settings.discord_webhook_url, error_message)


def build_meta_message(
    source_name: str,
    fetched_title: str,
    url: str,
    summary: str,
    classification: str,
    safety_review: str,
) -> str:
    return (
        "## 新規下書き候補\n"
        f"**source_name**: {source_name}\n"
        f"**fetched_title**: {fetched_title}\n"
        f"**url**: {url}\n\n"
        "### 要約\n"
        f"{summary}\n\n"
        "### 状態分類\n"
        f"{classification}\n\n"
        "### 安全点検\n"
        f"{safety_review}"
    )


if __name__ == "__main__":
    main()