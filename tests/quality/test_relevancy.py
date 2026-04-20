from allure import description

THRESHOLD = 0.70
THRESHOLD_QUICK = 0.65
MIN_CATEGORY = 0.55


class TestRelevancy:
    """Verify that agent answers are relevant to the asked questions."""

    @description("Overall answer relevancy >= 0.70")
    def test_qal_04(self, ragas_result):
        score = ragas_result["answer_relevancy"]

        assert score >= THRESHOLD, (
            f"Answer relevancy {score:.3f} < {THRESHOLD}. "
            f"Answers are not addressing the questions asked."
        )

    @description("Quick answer relevancy >= 0.65 (5 examples, CI)")
    def test_qal_05(self, ragas_result_quick):
        score = ragas_result_quick["answer_relevancy"]

        assert score >= THRESHOLD_QUICK, (
            f"Quick answer relevancy {score:.3f} < {THRESHOLD_QUICK}."
        )

    @description("No category has relevancy < 0.55")
    def test_qal_06(self, ragas_per_category):
        for cat, scores in ragas_per_category.items():
            assert scores["answer_relevancy"] >= MIN_CATEGORY, (
                f"Relevancy for '{cat}' = {scores['answer_relevancy']:.3f} < {MIN_CATEGORY}."
            )
