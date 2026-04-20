import logging

import pytest
from allure import description

from app.embeddings import SentenceTransformerProvider
from app.rag import QdrantRetriever, get_qdrant_client


@pytest.fixture(scope="module")
def _retriever():
    provider = SentenceTransformerProvider()
    client = get_qdrant_client()
    return QdrantRetriever(
        embedding_provider=provider,
        collection="fastapi_docs",
        qdrant_client=client,
    )


class TestLogging:
    """Verify that application produces correct structured logs."""

    @description("Retriever logs 'retriever_search' with latency_ms")
    def test_obs_01(self, _retriever, caplog):
        with caplog.at_level(logging.INFO, logger="app.rag"):
            _retriever.retrieve("CORS middleware", top_k=2)

        messages = [r.message for r in caplog.records]
        search_logs = [m for m in messages if "retriever_search" in m]
        assert len(search_logs) > 0, f"No 'retriever_search' log found. Got: {messages}"

    @description("Retriever logs 'retriever_found' with count and score")
    def test_obs_02(self, _retriever, caplog):
        with caplog.at_level(logging.INFO, logger="app.rag"):
            _retriever.retrieve("FastAPI routing", top_k=3)

        messages = [r.message for r in caplog.records]
        found_logs = [m for m in messages if "retriever_found" in m]
        assert len(found_logs) > 0, f"No 'retriever_found' log found. Got: {messages}"
        assert "count=" in found_logs[0]
        assert "best_score=" in found_logs[0]

    @description("latency_ms is present and > 0")
    def test_obs_03(self, _retriever, caplog):
        with caplog.at_level(logging.INFO, logger="app.rag"):
            _retriever.retrieve("dependency injection", top_k=1)

        messages = [r.message for r in caplog.records]
        search_logs = [m for m in messages if "latency_ms=" in m]
        assert len(search_logs) > 0, "No log with latency_ms found"

        for log_msg in search_logs:
            latency_part = [p for p in log_msg.split() if p.startswith("latency_ms=")]
            assert len(latency_part) > 0
            value = float(latency_part[0].split("=")[1])
            assert value > 0, f"latency_ms should be > 0, got {value}"

    @description("All log records have INFO level (no ERROR on success)")
    def test_obs_04(self, _retriever, caplog):
        with caplog.at_level(logging.DEBUG, logger="app.rag"):
            _retriever.retrieve("error handling", top_k=2)

        error_records = [r for r in caplog.records if r.levelno >= logging.ERROR]
        assert len(error_records) == 0, (
            f"Unexpected ERROR logs: {[r.message for r in error_records]}"
        )

    @description("Log records contain logger name 'app.rag'")
    def test_obs_05(self, _retriever, caplog):
        with caplog.at_level(logging.INFO, logger="app.rag"):
            _retriever.retrieve("middleware", top_k=1)

        assert len(caplog.records) > 0, "No logs captured"
        for record in caplog.records:
            assert record.name == "app.rag", f"Unexpected logger: {record.name}"
