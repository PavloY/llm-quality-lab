from app.embeddings import EmbeddingProvider
from app.rag import QdrantRetriever, get_qdrant_client
from app.schemas import RetrievalResult


class ToolKit:
    """Collection of tools that an agent can call."""

    def __init__(self, embedding_provider: EmbeddingProvider) -> None:
        self._client = get_qdrant_client()
        self._embedding = embedding_provider

    def _retriever(self, collection: str) -> QdrantRetriever:
        return QdrantRetriever(
            embedding_provider=self._embedding,
            collection=collection,
            qdrant_client=self._client,
        )

    def search_docs(self, query: str, top_k: int = 5) -> list[RetrievalResult]:
        """Search FastAPI documentation."""
        return self._retriever("fastapi_docs").retrieve(query, top_k=top_k)

    def search_troubleshoot(self, query: str, top_k: int = 5) -> list[RetrievalResult]:
        """Search troubleshooting guides."""
        return self._retriever("troubleshooting").retrieve(query, top_k=top_k)

    def search_faq(self, query: str, top_k: int = 3) -> list[RetrievalResult]:
        """Search FAQ."""
        return self._retriever("faq").retrieve(query, top_k=top_k)

    def no_search_needed(self) -> list[RetrievalResult]:
        """Use when the question can be answered without searching."""
        return [RetrievalResult(text="No search performed", source="agent_knowledge", score=1.0)]

    def get_tools(self) -> dict:
        """Return tool name → callable mapping."""
        return {
            "search_docs": self.search_docs,
            "search_troubleshoot": self.search_troubleshoot,
            "search_faq": self.search_faq,
            "no_search_needed": self.no_search_needed,
        }


TOOLS_DESCRIPTION = [
    {
        "type": "function",
        "function": {
            "name": "search_docs",
            "description": "Search FastAPI documentation for how things work, features, API reference",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "top_k": {"type": "integer", "description": "Number of results", "default": 5},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_troubleshoot",
            "description": "Search troubleshooting guides for errors, bugs, things not working",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "top_k": {"type": "integer", "description": "Number of results", "default": 5},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_faq",
            "description": "Search FAQ for general questions, comparisons, best practices",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "top_k": {"type": "integer", "description": "Number of results", "default": 3},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "no_search_needed",
            "description": "Use when the question is a greeting or can be answered without searching knowledge base",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]
