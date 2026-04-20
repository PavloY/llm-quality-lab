import pytest
from allure import description

from tests.helpers import assert_results_contain


class TestTroubleshootingRetrieval:
    """Verify semantic search in troubleshooting collection."""

    @pytest.fixture(autouse=True)
    def setup(self, make_retriever):
        self.retriever = make_retriever("troubleshooting")

    @description("'422 error' query finds validation content in troubleshooting")
    def test_ret_02(self):
        results = self.retriever.retrieve("422 validation error", top_k=5)

        assert len(results) > 0, "No results returned"
        assert_results_contain(results, "422")
