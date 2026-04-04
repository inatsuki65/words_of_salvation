from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.fetcher import FetchedSource
from app.llm_client import LLMClient


PROMPT_DIR = Path(__file__).parent / "prompts"


@dataclass
class PipelineResult:
    summary: str
    meaning: str
    targets: str
    classification: str
    blog_markdown: str
    personal_words: str
    image_prompt: str
    safety_review: str


def run_pipeline(llm: LLMClient, fetched: FetchedSource) -> PipelineResult:
    summary = _run_step(
        llm,
        "summarize.md",
        {"input": fetched.raw_text[:30000]},
    )

    meaning = _run_step(
        llm,
        "meaning.md",
        {"summary": summary},
    )

    targets = _run_step(
        llm,
        "targets.md",
        {"analysis": meaning},
    )

    classification = _run_step(
        llm,
        "classify_states.md",
        {"analysis": meaning + "\n\n" + targets},
    )

    blog_markdown = _run_step(
        llm,
        "blog.md",
        {
            "summary": summary,
            "analysis": meaning,
            "targets": targets,
            "source_title": fetched.title,
            "source_url": fetched.url,
        },
    )

    personal_words = _run_step(
        llm,
        "personal_words.md",
        {
            "targets": targets,
            "classification": classification,
            "source_title": fetched.title,
        },
    )

    image_prompt = _run_step(
        llm,
        "image_prompt.md",
        {"article_markdown": blog_markdown},
    )

    safety_review = _run_step(
        llm,
        "safety.md",
        {
            "draft": blog_markdown + "\n\n" + personal_words,
        },
    )

    return PipelineResult(
        summary=summary,
        meaning=meaning,
        targets=targets,
        classification=classification,
        blog_markdown=blog_markdown,
        personal_words=personal_words,
        image_prompt=image_prompt,
        safety_review=safety_review,
    )


def _run_step(llm: LLMClient, prompt_filename: str, variables: dict[str, str]) -> str:
    template = (PROMPT_DIR / prompt_filename).read_text(encoding="utf-8")
    prompt = llm.render_prompt(template, variables)
    return llm.complete(prompt)