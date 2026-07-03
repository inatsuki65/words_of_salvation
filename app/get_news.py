import json

import feedparser
import requests

from app.config import SOURCES_JSON


def update_sources_json() -> None:
    keyword = "自殺 OR 自死 OR suicide"

    encoded = requests.utils.quote(keyword)

    rss_url = (
        "https://news.google.com/rss/search?"
        f"q={encoded}&hl=ja&gl=JP&ceid=JP:ja"
    )

    feed = feedparser.parse(rss_url)

    if not feed.entries:
        print("ニュースがありません。")
        return

    latest = max(
        feed.entries,
        key=lambda x: x.get("published_parsed", (0,))
    )

    source = {
        "name": latest.title,
        "url": latest.link,
        "type": "web"
    }

    SOURCES_JSON.parent.mkdir(parents=True, exist_ok=True)

    with SOURCES_JSON.open("w", encoding="utf-8") as f:
        json.dump([source], f, ensure_ascii=False, indent=2)

    print("sources.json を更新しました。")
    print("タイトル:", latest.title)
    print("リンク:", latest.link)
    print("公開日時:", latest.get("published", "不明"))


if __name__ == "__main__":
    update_sources_json()