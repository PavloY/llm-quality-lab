import pytest

from app.embeddings import SentenceTransformerProvider
from app.rag import get_qdrant_client


@pytest.fixture(scope="session")
def embedding_provider():
    """Shared embedding provider — loads model once for all tests."""
    return SentenceTransformerProvider()


@pytest.fixture(scope="session")
def qdrant_client():
    """Shared Qdrant client — avoids file locking issues with local storage."""
    return get_qdrant_client()
