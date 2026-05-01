from __future__ import annotations

import json
from typing import Protocol

from openai import OpenAI

from app.config import settings
from app.schemas import AssistantMessage, LLMToolResponse, ToolCall


class LLMProvider(Protocol):
    """Contract for any LLM provider."""

    def generate(
        self, prompt: str, system_prompt: str, temperature: float, max_tokens: int
    ) -> str: ...

    def generate_structured(self, prompt: str, system_prompt: str, temperature: float) -> str: ...

    def generate_with_tools(
        self,
        messages: list[dict],
        tools: list[dict],
        temperature: float,
        max_tokens: int,
    ) -> LLMToolResponse: ...


_OPENAI_FINISH_MAP = {
    "stop": "end_turn",
    "tool_calls": "tool_use",
    "length": "max_tokens",
    "content_filter": "other",
    "function_call": "tool_use",
}


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

    def generate_with_tools(
        self,
        messages: list[dict],
        tools: list[dict],
        temperature: float = 0.0,
        max_tokens: int = 1024,
    ) -> LLMToolResponse:
        """Tool-calling generation. Returns provider-neutral LLMToolResponse."""
        response = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=temperature,
            max_tokens=max_tokens,
        )
        choice = response.choices[0]
        msg = choice.message

        tool_calls: list[ToolCall] = []
        if msg.tool_calls:
            for tc in msg.tool_calls:
                try:
                    args = json.loads(tc.function.arguments)
                except json.JSONDecodeError:
                    args = {}
                tool_calls.append(ToolCall(id=tc.id, name=tc.function.name, arguments=args))

        stop_reason = _OPENAI_FINISH_MAP.get(choice.finish_reason or "stop", "other")
        usage = response.usage
        return LLMToolResponse(
            message=AssistantMessage(content=msg.content, tool_calls=tool_calls),
            stop_reason=stop_reason,
            tokens_in=usage.prompt_tokens if usage else 0,
            tokens_out=usage.completion_tokens if usage else 0,
        )
