import pytest
from allure import description
from pydantic import ValidationError

from app.schemas import QueryRoute


class TestQueryRoute:
    """Verify QueryRoute Literal and confidence constraints."""

    @description("QueryRoute accepts valid intent, confidence, reasoning")
    def test_sch_07(self):
        route = QueryRoute(intent="docs", confidence=0.9, reasoning="About features")

        assert route.intent == "docs"
        assert route.confidence == 0.9

    @description("QueryRoute accepts all three valid intents: docs, troubleshooting, faq")
    def test_sch_08(self):
        for intent in ("docs", "troubleshooting", "faq"):
            route = QueryRoute(intent=intent, confidence=0.8, reasoning="test")

            assert route.intent == intent

    @description("QueryRoute rejects invalid intent 'pizza'")
    def test_sch_09(self):
        with pytest.raises(ValidationError) as exc_info:
            QueryRoute(intent="pizza", confidence=0.5, reasoning="test")

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("intent",) for e in errors)

    @description("QueryRoute rejects confidence > 1.0")
    def test_sch_10(self):
        with pytest.raises(ValidationError):
            QueryRoute(intent="docs", confidence=1.5, reasoning="test")

    @description("QueryRoute rejects confidence < 0.0")
    def test_sch_11(self):
        with pytest.raises(ValidationError):
            QueryRoute(intent="faq", confidence=-0.1, reasoning="test")
