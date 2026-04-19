import json

from app.llm import LLMProvider
from app.schemas import QueryRoute

ROUTER_SYSTEM_PROMPT = """You are a query classifier. Classify the user's question into one of these categories:
- "docs": questions about how FastAPI works, features, API reference, syntax, examples
- "troubleshooting": questions about errors, bugs, things not working, debugging, performance issues
- "faq": general questions, comparisons, best practices, "how to" questions, recommendations

Respond ONLY with valid JSON in this exact format:
{"intent": "docs|troubleshooting|faq", "confidence": 0.0-1.0, "reasoning": "brief explanation"}

Examples:
- "How does dependency injection work?" -> {"intent": "docs", "confidence": 0.95, "reasoning": "Question about a specific FastAPI feature"}
- "Why am I getting a 422 error?" -> {"intent": "troubleshooting", "confidence": 0.9, "reasoning": "User is experiencing an error"}
- "Should I use FastAPI or Flask?" -> {"intent": "faq", "confidence": 0.85, "reasoning": "General comparison question"}"""


class QueryRouter:
    """Classifies user questions to determine which KB to search."""

    def __init__(self, llm_provider: LLMProvider) -> None:
        self._llm = llm_provider

    def classify(self, question: str) -> QueryRoute:
        """Classify a question and return a structured route."""
        response = self._llm.generate(
            prompt=question,
            system_prompt=ROUTER_SYSTEM_PROMPT,
            temperature=0.0,
        )

        try:
            data = json.loads(response)
            return QueryRoute(**data)
        except (json.JSONDecodeError, Exception):
            return QueryRoute(
                intent="docs",
                confidence=0.5,
                reasoning="Fallback to docs (classification failed)",
            )
