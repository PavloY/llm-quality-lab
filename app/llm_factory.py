"""LLM factory — switches provider based on LLM_PROVIDER env var.

- role="main"  → agent/router
- role="judge" → Ragas/safety evaluator
"""

from __future__ import annotations

import os

from dotenv import load_dotenv

from app.llm import LLMProvider, OpenAIProvider

load_dotenv()


def _kind() -> str:
    return os.environ.get("LLM_PROVIDER", "openai").lower().strip()


def get_llm(role: str = "main") -> LLMProvider:
    if _kind() == "bedrock":
        from app._private.alt_provider import AltProvider

        return AltProvider(role=role)
    return OpenAIProvider()


def get_ragas_config() -> dict:
    """Return {llm, embeddings} overrides for Ragas evaluate().

    Default provider: Ragas uses its built-in OpenAI defaults → returns Nones.
    Alt provider: returns a judge-role LLM + local-embeddings adapter.
    """
    if _kind() == "bedrock":
        from app._private.ragas_alt_patch import (
            build_ragas_embeddings,
            build_ragas_judge_llm,
        )
        from app.embeddings import SentenceTransformerProvider

        return {
            "llm": build_ragas_judge_llm(),
            "embeddings": build_ragas_embeddings(SentenceTransformerProvider()),
        }
    return {"llm": None, "embeddings": None}
