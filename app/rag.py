from qdrant_client import QdrantClient

from app.config import settings
from app.embeddings import EmbeddingProvider
from app.llm import LLMProvider
from app.logging_config import get_logger, log_timing
from app.router import QueryRouter
from app.schemas import RAGResponse, RetrievalResult

logger = get_logger(__name__)

DEFAULT_COLLECTION = "fastapi_docs"
DEFAULT_TOP_K = 5

RAG_SYSTEM_PROMPT = """You are a technical support assistant for FastAPI documentation.
Answer ONLY based on the provided context. If the answer is not in the context, say:
"I don't have this information in the knowledge base."
Always respond in the same language as the question."""


def get_qdrant_client(qdrant_path: str = settings.qdrant_path) -> QdrantClient:
    """Get or create a shared Qdrant client for the given path."""
    if not hasattr(get_qdrant_client, "_instances"):
        get_qdrant_client._instances = {}
    if qdrant_path not in get_qdrant_client._instances:
        get_qdrant_client._instances[qdrant_path] = QdrantClient(path=qdrant_path)
    return get_qdrant_client._instances[qdrant_path]


class QdrantRetriever:
    """Retrieves relevant document chunks from Qdrant using vector similarity."""

    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        collection: str = DEFAULT_COLLECTION,
        qdrant_client: QdrantClient | None = None,
    ) -> None:
        self._embedding_provider = embedding_provider
        self._collection = collection
        self._client = qdrant_client or get_qdrant_client()

    def retrieve(self, query: str, top_k: int = DEFAULT_TOP_K) -> list[RetrievalResult]:
        """Search for the most relevant chunks given a natural language query."""
        with log_timing(logger, "retriever_search", collection=self._collection, query=f"'{query}'"):
            query_vector = self._embedding_provider.embed_text(query)

            hits = self._client.search(
                collection_name=self._collection,
                query_vector=query_vector,
                limit=top_k,
            )

            results = [
                RetrievalResult(
                    text=hit.payload["text"],
                    source=hit.payload["source"],
                    score=hit.score,
                )
                for hit in hits
            ]

        if results:
            logger.info("retriever_found count=%d best_score=%.4f best_source=%s", len(results), results[0].score, results[0].source)
        else:
            logger.warning("retriever_empty query='%s'", query)
        return results


class RAGPipeline:
    """Full RAG pipeline: retrieve context, then generate answer via LLM."""

    def __init__(self, retriever: QdrantRetriever, llm_provider: LLMProvider) -> None:
        self._retriever = retriever
        self._llm = llm_provider

    def generate_answer(self, question: str, top_k: int = DEFAULT_TOP_K) -> RAGResponse:
        """Retrieve relevant chunks and generate an answer based on them."""
        logger.info("RAG: generating answer for '%s'", question)
        chunks = self._retriever.retrieve(query=question, top_k=top_k)

        if not chunks:
            logger.warning("RAG: no chunks found, returning empty response")
            return RAGResponse(
                answer="No relevant documents found.",
                sources=[],
                chunks_used=0,
            )

        context = "\n\n---\n\n".join([c.text for c in chunks])
        prompt = f"Context:\n{context}\n\nQuestion: {question}"

        logger.info("RAG: sending %d chunks to LLM", len(chunks))
        answer = self._llm.generate(prompt=prompt, system_prompt=RAG_SYSTEM_PROMPT)

        sources = list({c.source for c in chunks})
        logger.info("RAG: answer generated, sources=%s", sources)
        return RAGResponse(
            answer=answer,
            sources=sources,
            chunks_used=len(chunks),
        )


COLLECTION_MAP = {
    "docs": "fastapi_docs",
    "troubleshooting": "troubleshooting",
    "faq": "faq",
}


class RoutedRAGPipeline:
    """RAG pipeline with automatic KB routing based on question classification."""

    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        llm_provider: LLMProvider,
        qdrant_client: QdrantClient | None = None,
    ) -> None:
        self._embedding_provider = embedding_provider
        self._llm = llm_provider
        self._client = qdrant_client or get_qdrant_client()
        self._router = QueryRouter(llm_provider=llm_provider)

    def answer(self, question: str, top_k: int = DEFAULT_TOP_K) -> RAGResponse:
        """Classify question, route to correct KB, retrieve, and generate answer."""
        route = self._router.classify(question)
        collection = COLLECTION_MAP[route.intent]
        logger.info("RoutedRAG: routed to '%s' (confidence=%.2f)", route.intent, route.confidence)

        retriever = QdrantRetriever(
            embedding_provider=self._embedding_provider,
            collection=collection,
            qdrant_client=self._client,
        )
        pipeline = RAGPipeline(retriever=retriever, llm_provider=self._llm)
        result = pipeline.generate_answer(question=question, top_k=top_k)
        result.route = route
        return result
