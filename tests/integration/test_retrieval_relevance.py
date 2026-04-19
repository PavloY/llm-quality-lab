from app.rag import QdrantRetriever


def test_cors_query_finds_middleware(embedding_provider, qdrant_client):
    """Query about CORS should find the CORS middleware chunk."""
    retriever = QdrantRetriever(
        embedding_provider=embedding_provider,
        collection="fastapi_docs",
        qdrant_client=qdrant_client,
    )
    results = retriever.retrieve("CORS middleware", top_k=5)

    assert len(results) > 0, "No results returned"
    texts = " ".join(r.text for r in results)
    assert "CORSMiddleware" in texts, (
        f"None of the top-5 results contain 'CORSMiddleware'.\n"
        f"Sources: {[r.source for r in results]}"
    )


def test_error_422_finds_troubleshooting(embedding_provider, qdrant_client):
    """Query about 422 error in troubleshooting should find validation content."""
    retriever = QdrantRetriever(
        embedding_provider=embedding_provider,
        collection="troubleshooting",
        qdrant_client=qdrant_client,
    )
    results = retriever.retrieve("422 validation error", top_k=5)

    assert len(results) > 0, "No results returned"
    texts = " ".join(r.text.lower() for r in results)
    assert "validat" in texts or "422" in texts or "pydantic" in texts, (
        f"No validation-related content found.\n"
        f"Sources: {[r.source for r in results]}"
    )


def test_faq_finds_comparison(embedding_provider, qdrant_client):
    """Query about framework comparison should find FAQ content."""
    retriever = QdrantRetriever(
        embedding_provider=embedding_provider,
        collection="faq",
        qdrant_client=qdrant_client,
    )
    results = retriever.retrieve("FastAPI vs Flask comparison", top_k=5)

    assert len(results) > 0, "No results returned"
    texts = " ".join(r.text.lower() for r in results)
    assert "flask" in texts, (
        f"No Flask comparison content found.\n"
        f"Sources: {[r.source for r in results]}"
    )


def test_top_k_limits_results(embedding_provider, qdrant_client):
    """top_k parameter should limit the number of returned results."""
    retriever = QdrantRetriever(
        embedding_provider=embedding_provider,
        collection="fastapi_docs",
        qdrant_client=qdrant_client,
    )
    results = retriever.retrieve("FastAPI", top_k=2)

    assert len(results) == 2, f"Expected 2 results with top_k=2, got {len(results)}"


def test_irrelevant_query_returns_low_scores(embedding_provider, qdrant_client):
    """A completely off-topic query should get low similarity scores."""
    retriever = QdrantRetriever(
        embedding_provider=embedding_provider,
        collection="fastapi_docs",
        qdrant_client=qdrant_client,
    )
    results = retriever.retrieve("quantum physics black hole entropy", top_k=3)

    assert len(results) > 0
    for r in results:
        assert r.score < 0.5, (
            f"Irrelevant query got score {r.score:.4f} from {r.source}. "
            f"Expected < 0.5 for off-topic query."
        )


def test_result_fields_are_typed(embedding_provider, qdrant_client):
    """Each result should be a RetrievalResult with correct field types."""
    from app.schemas import RetrievalResult

    retriever = QdrantRetriever(
        embedding_provider=embedding_provider,
        collection="fastapi_docs",
        qdrant_client=qdrant_client,
    )
    results = retriever.retrieve("routing", top_k=1)

    assert len(results) == 1
    result = results[0]
    assert isinstance(result, RetrievalResult)
    assert isinstance(result.text, str)
    assert isinstance(result.source, str)
    assert isinstance(result.score, float)
    assert 0.0 <= result.score <= 1.0
