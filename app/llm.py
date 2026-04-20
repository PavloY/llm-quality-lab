from typing import Protocol

from openai import OpenAI

from app.config import settings


class LLMProvider(Protocol):
    """Contract for any LLM provider."""

    def generate(
        self, prompt: str, system_prompt: str, temperature: float, max_tokens: int
    ) -> str: ...

    def generate_structured(self, prompt: str, system_prompt: str, temperature: float) -> str: ...


class OpenAIProvider:
    """LLM provider using OpenAI-compatible API (OpenAI, OpenRouter, etc.)."""

    def __init__(
        self,
        api_key: str = settings.llm_api_key,
        base_url: str = settings.llm_base_url,
        model: str = settings.llm_model,
    ) -> None:
        self._client = OpenAI(api_key=api_key, base_url=base_url)
        self._model = model

    def generate(
        self,
        prompt: str,
        system_prompt: str = "You are a helpful technical assistant.",
        temperature: float = 0.0,
        max_tokens: int = 1024,
    ) -> str:
        """Generate a text response from the LLM."""
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content

    def generate_structured(
        self,
        prompt: str,
        system_prompt: str = "You are a helpful assistant. Respond with valid JSON only.",
        temperature: float = 0.0,
    ) -> str:
        """Generate a JSON response from the LLM."""
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
            response_format={"type": "json_object"},
        )
        return response.choices[0].message.content
