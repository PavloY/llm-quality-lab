from allure import description

THRESHOLD = 0.70
THRESHOLD_QUICK = 0.65
MIN_CATEGORY = 0.50


class TestContextRecall:
    """Verify that retrieval finds chunks covering ground truth facts."""

    @description("Overall context recall >= 0.70")
    def test_qal_07(self, ragas_result):
        score = ragas_result["context_recall"]

        assert score >= THRESHOLD, (
            f"Context recall {score:.3f} < {THRESHOLD}. "
            f"Retrieval is missing relevant context."
        )

    @description("Quick context recall >= 0.65 (5 examples, CI)")
    def test_qal_08(self, ragas_result_quick):
        score = ragas_result_quick["context_recall"]

        assert score >= THRESHOLD_QUICK, (
            f"Quick context recall {score:.3f} < {THRESHOLD_QUICK}."
        )

    @description("No category has context recall < 0.50")
    def test_qal_09(self, ragas_per_category):
        for cat, scores in ragas_per_category.items():
            assert scores["context_recall"] >= MIN_CATEGORY, (
                f"Context recall for '{cat}' = {scores['context_recall']:.3f} < {MIN_CATEGORY}."
            )
