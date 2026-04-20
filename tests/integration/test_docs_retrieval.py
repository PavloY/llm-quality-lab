import pytest
from allure import description

from app.schemas import RetrievalResult
from tests.helpers import assert_results_contain


class TestDocsRetrieval:
    """Verify semantic search in fastapi_docs collection."""

    @pytest.fixture(autouse=True)
    def setup(self, make_retriever):
        self.retriever = make_retriever("fastapi_docs")

    @description("'CORS middleware' query finds CORSMiddleware in docs")
    def test_ret_01(self):
        results = self.retriever.retrieve("CORS middleware", top_k=5)

        assert len(results) > 0, "No results returned"
        assert_results_contain(results, "CORSMiddleware")

    @description("top_k=2 returns exactly 2 results")
    def test_ret_04(self):
        results = self.retriever.retrieve("FastAPI", top_k=2)

        assert len(results) == 2, f"Expected 2, got {len(results)}"

    @description("Off-topic query gets score < 0.5 for all results")
    def test_ret_05(self):
        results = self.retriever.retrieve("quantum physics black hole entropy", top_k=3)

        assert len(results) > 0
        for r in results:
            assert r.score < 0.5, f"Off-topic got score {r.score:.4f} from {r.source}"

    @description("Results are typed RetrievalResult with correct field types")
    def test_ret_06(self):
        results = self.retriever.retrieve("routing", top_k=1)

        assert len(results) == 1
        result = results[0]
        assert isinstance(result, RetrievalResult)
        assert isinstance(result.text, str)
        assert isinstance(result.source, str)
        assert isinstance(result.score, float)
        assert 0.0 <= result.score <= 1.0
