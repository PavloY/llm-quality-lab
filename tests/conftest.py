from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.embeddings import SentenceTransformerProvider
from app.main import app
from app.rag import QdrantRetriever, get_qdrant_client
from app.schemas import AgentResponse, AgentStep
from app.tools import ToolKit
from tests.helpers import LoggingClient, LoggingRetriever

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
