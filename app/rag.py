from qdrant_client import QdrantClient

from app.config import settings
from app.embeddings import EmbeddingProvider
from app.schemas import RetrievalResult

DEFAULT_COLLECTION = "fastapi_docs"
DEFAULT_TOP_K = 5


class QdrantRetriever:
    """Retrieves relevant document chunks from Qdrant using vector similarity."""

    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        collection: str = DEFAULT_COLLECTION,
        qdrant_path: str = settings.qdrant_path,
    ) -> None:
        self._embedding_provider = embedding_provider
        self._collection = collection
        self._client = QdrantClient(path=qdrant_path)

    def retrieve(self, query: str, top_k: int = DEFAULT_TOP_K) -> list[RetrievalResult]:
        """Search for the most relevant chunks given a natural language query."""
        query_vector = self._embedding_provider.embed_text(query)

        hits = self._client.search(
            collection_name=self._collection,
            query_vector=query_vector,
            limit=top_k,
        )

        return [
            RetrievalResult(
                text=hit.payload["text"],
                source=hit.payload["source"],
                score=hit.score,
            )
            for hit in hits
        ]
