from typing import Protocol

from sentence_transformers import SentenceTransformer

from app.config import settings


class EmbeddingProvider(Protocol):
    """Contract for any embedding provider."""

    def embed_text(self, text: str) -> list[float]: ...

    def embed_texts(self, texts: list[str]) -> list[list[float]]: ...


class SentenceTransformerProvider:
    """Embedding provider using sentence-transformers library."""

    def __init__(self, model_name: str = settings.embedding_model) -> None:
        self._model = SentenceTransformer(model_name)

    def embed_text(self, text: str) -> list[float]:
        return self._model.encode(text).tolist()

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return self._model.encode(texts).tolist()
