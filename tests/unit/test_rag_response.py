import pytest
from allure import description
from pydantic import ValidationError

from app.schemas import QueryRoute, RAGResponse


class TestRAGResponse:
    """Verify RAGResponse structure and optional fields."""

    @description("RAGResponse accepts valid fields, route defaults to None")
    def test_sch_12(self):
        response = RAGResponse(answer="answer", sources=["file.md"], chunks_used=3)

        assert response.answer == "answer"
        assert response.chunks_used == 3
        assert response.route is None

    @description("RAGResponse accepts optional QueryRoute")
    def test_sch_13(self):
        route = QueryRoute(intent="docs", confidence=0.9, reasoning="test")

        response = RAGResponse(answer="a", sources=["f.md"], chunks_used=1, route=route)

        assert response.route.intent == "docs"

    @description("RAGResponse rejects negative chunks_used")
    def test_sch_14(self):
        with pytest.raises(ValidationError):
            RAGResponse(answer="x", sources=[], chunks_used=-1)
