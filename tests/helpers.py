"""Shared test helpers — logging wrappers and assertion utilities."""

import logging

from app.rag import QdrantRetriever
from app.schemas import RetrievalResult

logger = logging.getLogger("tests")


class LoggingRetriever:
    """Decorator over QdrantRetriever that logs every retrieve() call."""

    def __init__(self, retriever: QdrantRetriever) -> None:
        self._retriever = retriever

    def retrieve(self, query: str, top_k: int = 5) -> list[RetrievalResult]:
        results = self._retriever.retrieve(query, top_k=top_k)
        for i, r in enumerate(results):
            logger.info(
                "  Result %d: source=%s score=%.4f text='%s...'",
                i + 1,
                r.source,
                r.score,
                r.text[:80],
            )
        return results


class LoggingClient:
    """Decorator over TestClient that logs every request/response."""

    def __init__(self, client) -> None:
        self._client = client

    def _log(self, method: str, url: str, response) -> None:
        try:
            body = response.json()
        except Exception:
            body = response.text
        logger.info("  %s %s → %d %s", method, url, response.status_code, body)

    def get(self, url: str, **kwargs):
        response = self._client.get(url, **kwargs)
        self._log("GET", url, response)
        return response

    def post(self, url: str, **kwargs):
        response = self._client.post(url, **kwargs)
        self._log("POST", url, response)
        return response


def assert_results_contain(results: list[RetrievalResult], keyword: str) -> None:
    """Assert that at least one result's text contains the keyword."""
    texts = " ".join(r.text.lower() for r in results)
    assert keyword.lower() in texts, (
        f"'{keyword}' not found in results. Sources: {[r.source for r in results]}"
    )
