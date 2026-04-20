from allure import description

THRESHOLD = 0.75
THRESHOLD_QUICK = 0.70
MIN_CATEGORY = 0.60


class TestFaithfulness:
    """Verify that agent answers are grounded in retrieved context."""

    @description("Overall faithfulness >= 0.75")
    def test_qal_01(self, ragas_result):
        score = ragas_result["faithfulness"]

        assert score >= THRESHOLD, (
            f"Faithfulness {score:.3f} < {THRESHOLD}. "
            f"Model is hallucinating — answers not grounded in context."
        )

    @description("Quick faithfulness >= 0.70 (5 examples, CI)")
    def test_qal_02(self, ragas_result_quick):
        score = ragas_result_quick["faithfulness"]

        assert score >= THRESHOLD_QUICK, (
            f"Quick faithfulness {score:.3f} < {THRESHOLD_QUICK}."
        )

    @description("No category has faithfulness < 0.60")
    def test_qal_03(self, ragas_per_category):
        for cat, scores in ragas_per_category.items():
            assert scores["faithfulness"] >= MIN_CATEGORY, (
                f"Faithfulness for '{cat}' = {scores['faithfulness']:.3f} < {MIN_CATEGORY}."
            )
