import logging

from allure import description

logger = logging.getLogger("tests.regression")

REGRESSION_TOLERANCE = 0.05
ABSOLUTE_THRESHOLDS = {
    "faithfulness": 0.70,
    "answer_relevancy": 0.65,
    "context_recall": 0.65,
}
LATENCY_TOLERANCE = 0.20


class TestPromptRegression:
    """Verify prompt v2 doesn't regress quality vs v1 baseline."""

    @description("Faithfulness v2 >= v1 - 0.05 (no regression)")
    def test_reg_01(self, v1_scores, v2_scores):
        v1 = v1_scores["faithfulness"]
        v2 = v2_scores["faithfulness"]
        delta = v2 - v1
        logger.info("faithfulness: v1=%.3f v2=%.3f delta=%.3f", v1, v2, delta)

        assert v2 >= v1 - REGRESSION_TOLERANCE, (
            f"Faithfulness regressed: v1={v1:.3f} v2={v2:.3f} delta={delta:.3f}"
        )

    @description("Relevancy v2 >= v1 - 0.05 (no regression)")
    def test_reg_02(self, v1_scores, v2_scores):
        v1 = v1_scores["answer_relevancy"]
        v2 = v2_scores["answer_relevancy"]
        delta = v2 - v1
        logger.info("relevancy: v1=%.3f v2=%.3f delta=%.3f", v1, v2, delta)

        assert v2 >= v1 - REGRESSION_TOLERANCE, (
            f"Relevancy regressed: v1={v1:.3f} v2={v2:.3f} delta={delta:.3f}"
        )

    @description("Context recall v2 >= v1 - 0.05 (no regression)")
    def test_reg_03(self, v1_scores, v2_scores):
        v1 = v1_scores["context_recall"]
        v2 = v2_scores["context_recall"]
        delta = v2 - v1
        logger.info("context_recall: v1=%.3f v2=%.3f delta=%.3f", v1, v2, delta)

        assert v2 >= v1 - REGRESSION_TOLERANCE, (
            f"Context recall regressed: v1={v1:.3f} v2={v2:.3f} delta={delta:.3f}"
        )

    @description("v2 latency p95 not worse than v1 + 20%")
    def test_reg_04(self, v1_benchmark, v2_benchmark):
        v1_p95 = v1_benchmark["total_p95"]
        v2_p95 = v2_benchmark["total_p95"]
        threshold = v1_p95 * (1 + LATENCY_TOLERANCE)
        logger.info("p95: v1=%.2f v2=%.2f threshold=%.2f", v1_p95, v2_p95, threshold)

        assert v2_p95 <= threshold, (
            f"Latency regressed: v1 p95={v1_p95:.1f}s, v2 p95={v2_p95:.1f}s > {threshold:.1f}s"
        )

    @description("v2 passes absolute quality thresholds")
    def test_reg_05(self, v2_scores):
        for metric, threshold in ABSOLUTE_THRESHOLDS.items():
            score = v2_scores[metric]
            logger.info("%s: v2=%.3f threshold=%.3f", metric, score, threshold)
            assert score >= threshold, (
                f"v2 {metric}={score:.3f} < absolute threshold {threshold}"
            )
