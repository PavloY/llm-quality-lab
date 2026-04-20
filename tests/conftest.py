import logging
import os

# Silence noisy third-party progress bars and logs BEFORE any imports
os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

for noisy_logger in [
    "sentence_transformers",
    "sentence_transformers.SentenceTransformer",
    "httpx",
    "httpcore",
    "urllib3",
    "huggingface_hub",
    "transformers",
    "openai",
]:
    logging.getLogger(noisy_logger).setLevel(logging.WARNING)

from unittest.mock import MagicMock, patch  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.embeddings import SentenceTransformerProvider  # noqa: E402
from app.main import app  # noqa: E402
from app.rag import QdrantRetriever, get_qdrant_client  # noqa: E402
from app.schemas import AgentResponse, AgentStep  # noqa: E402
from app.tools import ToolKit  # noqa: E402
from tests.helpers import LoggingClient, LoggingRetriever  # noqa: E402

# --- Session-scoped: loaded once for all tests ---


@pytest.fixture(scope="session")
def embedding_provider():
    return SentenceTransformerProvider()


@pytest.fixture(scope="session")
def qdrant_client():
    return get_qdrant_client()


@pytest.fixture(scope="session")
def toolkit(embedding_provider):
    return ToolKit(embedding_provider=embedding_provider)


# --- Retriever factory ---


@pytest.fixture
def make_retriever(embedding_provider, qdrant_client):
    """Factory fixture: call with collection name to get a LoggingRetriever."""

    def _factory(collection: str) -> LoggingRetriever:
        retriever = QdrantRetriever(
            embedding_provider=embedding_provider,
            collection=collection,
            qdrant_client=qdrant_client,
        )
        return LoggingRetriever(retriever)

    return _factory


# --- FastAPI client ---


@pytest.fixture
def client():
    return LoggingClient(TestClient(app))


# --- Mocked Agent ---

MOCK_AGENT_RESPONSE = AgentResponse(
    steps=[
        AgentStep(
            thought="I need to search the docs",
            action="search_docs",
            action_input={"query": "test"},
            observation="Found some docs about testing",
        ),
    ],
    final_answer="Here is a test answer based on the docs.",
    sources=["test_doc.md"],
    total_steps=1,
    tools_used=["search_docs"],
)


@pytest.fixture
def mock_agent():
    """Patches Agent in app.main with a mock that returns MOCK_AGENT_RESPONSE."""
    with patch("app.main.Agent") as mock_cls:
        mock_instance = MagicMock()
        mock_instance.query.return_value = MOCK_AGENT_RESPONSE
        mock_cls.return_value = mock_instance
        yield mock_instance
