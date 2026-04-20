import pytest
from allure import description

from tests.helpers import assert_results_contain


class TestFaqRetrieval:
    """Verify semantic search in faq collection."""

    @pytest.fixture(autouse=True)
    def setup(self, make_retriever):
        self.retriever = make_retriever("faq")

    @description("'FastAPI vs Flask' query finds comparison in faq")
    def test_ret_03(self):
        results = self.retriever.retrieve("FastAPI vs Flask comparison", top_k=5)

        assert len(results) > 0, "No results returned"
        assert_results_contain(results, "flask")
