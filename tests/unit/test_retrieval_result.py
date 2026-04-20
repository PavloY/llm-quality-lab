import pytest
from allure import description
from pydantic import ValidationError

from app.schemas import RetrievalResult


class TestRetrievalResult:
    """Verify RetrievalResult score constraints."""

    @description("RetrievalResult accepts score 0.85 in valid range")
    def test_sch_03(self):
        result = RetrievalResult(text="content", source="file.md", score=0.85)

        assert result.score == 0.85

    @description("RetrievalResult rejects score > 1.0")
    def test_sch_04(self):
        with pytest.raises(ValidationError) as exc_info:
            RetrievalResult(text="x", source="x", score=1.5)

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("score",) for e in errors)

    @description("RetrievalResult rejects score < 0.0")
    def test_sch_05(self):
        with pytest.raises(ValidationError) as exc_info:
            RetrievalResult(text="x", source="x", score=-0.1)

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("score",) for e in errors)

    @description("RetrievalResult accepts boundary values 0.0 and 1.0")
    def test_sch_06(self):
        low = RetrievalResult(text="x", source="x", score=0.0)
        high = RetrievalResult(text="x", source="x", score=1.0)

        assert low.score == 0.0
        assert high.score == 1.0
