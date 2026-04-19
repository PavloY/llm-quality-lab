import pytest
from pydantic import ValidationError

from app.schemas import ChunkPayload, QueryRoute, RAGResponse, RetrievalResult


# --- ChunkPayload ---

def test_chunk_payload_valid():
    """ChunkPayload accepts all required fields."""
    chunk = ChunkPayload(text="some text", source="test.md", header="Intro")
    assert chunk.text == "some text"
    assert chunk.source == "test.md"
    assert chunk.header == "Intro"


def test_chunk_payload_rejects_missing_fields():
    """ChunkPayload requires text, source, and header."""
    with pytest.raises(ValidationError):
        ChunkPayload(text="some text")


# --- RetrievalResult ---

def test_retrieval_result_valid():
    """RetrievalResult accepts valid score in range [0, 1]."""
    result = RetrievalResult(text="content", source="file.md", score=0.85)
    assert result.score == 0.85


def test_retrieval_result_score_too_high():
    """RetrievalResult rejects score > 1.0."""
    with pytest.raises(ValidationError) as exc_info:
        RetrievalResult(text="x", source="x", score=1.5)
    errors = exc_info.value.errors()
    assert any(e["loc"] == ("score",) for e in errors)


def test_retrieval_result_score_too_low():
    """RetrievalResult rejects score < 0.0."""
    with pytest.raises(ValidationError) as exc_info:
        RetrievalResult(text="x", source="x", score=-0.1)
    errors = exc_info.value.errors()
    assert any(e["loc"] == ("score",) for e in errors)


def test_retrieval_result_boundary_values():
    """RetrievalResult accepts exact boundary values 0.0 and 1.0."""
    low = RetrievalResult(text="x", source="x", score=0.0)
    high = RetrievalResult(text="x", source="x", score=1.0)
    assert low.score == 0.0
    assert high.score == 1.0


# --- QueryRoute ---

def test_query_route_valid():
    """QueryRoute accepts valid intent, confidence, and reasoning."""
    route = QueryRoute(
        intent="docs",
        confidence=0.9,
        reasoning="Question about FastAPI features",
    )
    assert route.intent == "docs"
    assert route.confidence == 0.9


def test_query_route_all_intents():
    """QueryRoute accepts all three valid intents."""
    for intent in ("docs", "troubleshooting", "faq"):
        route = QueryRoute(intent=intent, confidence=0.8, reasoning="test")
        assert route.intent == intent


def test_query_route_invalid_intent():
    """QueryRoute rejects intents not in the Literal set."""
    with pytest.raises(ValidationError) as exc_info:
        QueryRoute(intent="invalid", confidence=0.5, reasoning="test")
    errors = exc_info.value.errors()
    assert any(e["loc"] == ("intent",) for e in errors)


def test_query_route_confidence_too_high():
    """QueryRoute rejects confidence > 1.0."""
    with pytest.raises(ValidationError):
        QueryRoute(intent="docs", confidence=1.5, reasoning="test")


def test_query_route_confidence_too_low():
    """QueryRoute rejects confidence < 0.0."""
    with pytest.raises(ValidationError):
        QueryRoute(intent="faq", confidence=-0.1, reasoning="test")


# --- RAGResponse ---

def test_rag_response_valid():
    """RAGResponse accepts valid fields."""
    response = RAGResponse(
        answer="Here is the answer",
        sources=["middleware.md"],
        chunks_used=3,
    )
    assert response.answer == "Here is the answer"
    assert response.chunks_used == 3
    assert response.route is None


def test_rag_response_with_route():
    """RAGResponse accepts optional route."""
    route = QueryRoute(intent="docs", confidence=0.9, reasoning="test")
    response = RAGResponse(
        answer="answer",
        sources=["file.md"],
        chunks_used=1,
        route=route,
    )
    assert response.route.intent == "docs"


def test_rag_response_rejects_negative_chunks():
    """RAGResponse rejects negative chunks_used."""
    with pytest.raises(ValidationError):
        RAGResponse(answer="x", sources=[], chunks_used=-1)
