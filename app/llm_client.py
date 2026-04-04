from __future__ import annotations

from pathlib import Path

from openai import OpenAI


class LLMClient:
    def __init__(self, api_key: str, model: str) -> None:
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def load_prompt(self, prompt_path: str) -> str:
        path = Path(prompt_path)
        return path.read_text(encoding="utf-8")

    def render_prompt(self, template: str, variables: dict[str, str]) -> str:
        rendered = template
        for key, value in variables.items():
            rendered = rendered.replace(f"{{{{{key}}}}}", value)
        return rendered

    def complete(self, prompt: str) -> str:
        response = self.client.responses.create(
            model=self.model,
            input=prompt,
        )
        return response.output_text.strip()