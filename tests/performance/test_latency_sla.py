from allure import description


class TestLatencySLA:
    """Verify agent meets latency and step count SLAs."""

    @description("p95 total latency < 10s")
    def test_per_01(self, benchmark):
        assert benchmark["total_p95"] < 10.0, (
            f"p95 = {benchmark['total_p95']:.1f}s > 10s SLA"
        )

    @description("Mean total latency < 5s")
    def test_per_02(self, benchmark):
        assert benchmark["total_mean"] < 5.0, (
            f"Mean = {benchmark['total_mean']:.1f}s > 5s SLA"
        )

    @description("Average agent steps <= 4")
    def test_per_03(self, benchmark):
        assert benchmark["avg_steps"] <= 4.0, (
            f"Avg steps = {benchmark['avg_steps']:.1f} > 4"
        )

    @description("Max steps <= 5 (MAX_STEPS limit works)")
    def test_per_04(self, benchmark):
        assert benchmark["max_steps"] <= 5, (
            f"Max steps = {benchmark['max_steps']} > 5"
        )

    @description("No single request > 30s (no runaway requests)")
    def test_per_05(self, benchmark):
        assert benchmark["total_max"] < 30.0, (
            f"Max = {benchmark['total_max']:.1f}s > 30s (runaway request)"
        )
