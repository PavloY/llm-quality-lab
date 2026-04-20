import logging

import allure

from app.rag import QdrantRetriever
from app.schemas import RetrievalResult

logger = logging.getLogger("tests")


class LoggingRetriever:
    """Decorator over QdrantRetriever — logs + allure.step on every retrieve()."""

    def __init__(self, retriever: QdrantRetriever) -> None:
        self._retriever = retriever

    def retrieve(self, query: str, top_k: int = 5) -> list[RetrievalResult]:
        with allure.step(f"Retrieve: '{query}' top_k={top_k}"):
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
    """Decorator over TestClient — logs + allure.step on every request."""

    def __init__(self, client) -> None:
        self._client = client

    def _log_and_step(self, method: str, url: str, response):
        try:
            body = response.json()
        except Exception:
            body = response.text
        logger.info("  %s %s → %d %s", method, url, response.status_code, body)

    def get(self, url: str, **kwargs):
        with allure.step(f"GET {url}"):
            response = self._client.get(url, **kwargs)
            self._log_and_step("GET", url, response)
            return response

    def post(self, url: str, **kwargs):
        with allure.step(f"POST {url}"):
            response = self._client.post(url, **kwargs)
            self._log_and_step("POST", url, response)
            return response


def assert_results_contain(results: list[RetrievalResult], keyword: str) -> None:
    """Assert that at least one result's text contains the keyword."""
    with allure.step(f"Assert results contain '{keyword}'"):
        texts = " ".join(r.text.lower() for r in results)
        assert keyword.lower() in texts, (
            f"'{keyword}' not found in results. Sources: {[r.source for r in results]}"
        )


def get_prompts_by_category(canary_prompts: list[dict], category: str) -> list[dict]:
    """Filter canary prompts by category."""
    return [p for p in canary_prompts if p["category"] == category]


def iterate_canary(canary_prompts: list[dict], category: str, make_agent):
    """Iterate canary prompts with allure.step for each. Yields (canary, result)."""
    prompts = get_prompts_by_category(canary_prompts, category)
    for canary in prompts:
        with allure.step(f"{canary['id']}: {canary['description']}"):
            agent = make_agent()
            result = agent.query(canary["prompt"])
            yield canary, result
