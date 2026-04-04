from __future__ import annotations

import io
from dataclasses import dataclass
from typing import Optional

import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader


@dataclass
class FetchedSource:
    title: str
    url: str
    source_type: str
    raw_text: str


class FetchError(Exception):
    pass


def fetch_source(url: str, source_type: str, timeout: int = 30) -> FetchedSource:
    if source_type == "pdf":
        return _fetch_pdf(url, timeout)
    if source_type == "web":
        return _fetch_web(url, timeout)
    raise FetchError(f"Unsupported source_type: {source_type}")


def _fetch_web(url: str, timeout: int) -> FetchedSource:
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    title = _extract_title(soup) or url
    raw_text = _extract_web_text(soup)

    if not raw_text.strip():
        raise FetchError(f"Could not extract text from webpage: {url}")

    return FetchedSource(
        title=title,
        url=url,
        source_type="web",
        raw_text=raw_text,
    )


def _fetch_pdf(url: str, timeout: int) -> FetchedSource:
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()

    pdf_stream = io.BytesIO(response.content)
    reader = PdfReader(pdf_stream)

    texts = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        texts.append(page_text)

    raw_text = "\n".join(texts).strip()
    if not raw_text:
        raise FetchError(f"Could not extract text from PDF: {url}")

    return FetchedSource(
        title=url.split("/")[-1] or url,
        url=url,
        source_type="pdf",
        raw_text=raw_text,
    )


def _extract_title(soup: BeautifulSoup) -> Optional[str]:
    if soup.title and soup.title.string:
        return soup.title.string.strip()
    og_title = soup.find("meta", attrs={"property": "og:title"})
    if og_title and og_title.get("content"):
        return og_title["content"].strip()
    return None


def _extract_web_text(soup: BeautifulSoup) -> str:
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    return "\n".join(lines)