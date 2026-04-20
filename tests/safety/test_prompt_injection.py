from allure import description

from tests.helpers import iterate_canary
from tests.safety.conftest import evaluate_stays_in_role


class TestPromptInjection:
    """Test agent resilience against prompt injection attacks."""

    @description("Agent ignores instruction override attempts (4 prompts)")
    def test_saf_01(self, canary_prompts, make_agent, safety_llm):
        for canary, result in iterate_canary(canary_prompts, "instruction_override", make_agent):
            assert evaluate_stays_in_role(canary["prompt"], result.final_answer, safety_llm), (
                f"Agent left role on: {canary['id']}"
            )

    @description("Agent rejects role hijack attempts (3 prompts)")
    def test_saf_02(self, canary_prompts, make_agent, safety_llm):
        for canary, result in iterate_canary(canary_prompts, "role_hijack", make_agent):
            assert evaluate_stays_in_role(canary["prompt"], result.final_answer, safety_llm), (
                f"Agent was hijacked by: {canary['id']}"
            )

    @description("Agent resists social engineering (3 prompts)")
    def test_saf_03(self, canary_prompts, make_agent, safety_llm):
        for canary, result in iterate_canary(canary_prompts, "social_engineering", make_agent):
            assert evaluate_stays_in_role(canary["prompt"], result.final_answer, safety_llm), (
                f"Agent fell for: {canary['id']}"
            )
