import json
import logging
import sys
from pathlib import Path

import pytest
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import answer_relevancy, context_recall, faithfulness

import app.agent as agent_module
from app.agent import Agent
from app.embeddings import SentenceTransformerProvider
from app.llm import OpenAIProvider
from app.tools import ToolKit

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "scripts"))
from benchmark import run_benchmark

logger = logging.getLogger("tests.regression")

GOLDEN_QUICK_PATH = "data/golden_examples_quick.json"


def _load_prompt(version: str) -> str:
    path = Path(f"configs/prompt_{version}.txt")
    return path.read_text(encoding="utf-8").strip()


def _run_evaluation_with_prompt(prompt_text: str) -> dict:
    """Run Ragas evaluation with a specific system prompt."""
    original_prompt = agent_module.AGENT_SYSTEM_PROMPT
    agent_module.AGENT_SYSTEM_PROMPT = prompt_text

    try:
        provider = SentenceTransformerProvider()
        llm = OpenAIProvider()
        toolkit = ToolKit(embedding_provider=provider)

        with open(GOLDEN_QUICK_PATH) as f:
            examples = json.load(f)

        questions, answers, contexts, ground_truths = [], [], [], []

        filtered = [ex for ex in examples if ex.get("category") != "out_of_scope"]
        logger.info("Regression eval: %d examples with prompt '%s...'", len(filtered), prompt_text[:40])

        for ex in filtered:
            agent = Agent(toolkit=toolkit, llm_provider=llm)
            result = agent.query(ex["question"])

            ctx = [step.observation for step in result.steps if step.observation]

            questions.append(ex["question"])
            answers.append(result.final_answer)
            contexts.append(ctx if ctx else ["No context"])
            ground_truths.append(ex["ground_truth"])

        dataset = Dataset.from_dict({
            "question": questions,
            "answer": answers,
            "contexts": contexts,
            "ground_truth": ground_truths,
        })

        result = evaluate(dataset, metrics=[faithfulness, answer_relevancy, context_recall])
        scores = dict(result)
        logger.info("Regression eval done: %s", scores)
        return scores
    finally:
        agent_module.AGENT_SYSTEM_PROMPT = original_prompt


def _run_benchmark_with_prompt(prompt_text: str) -> dict:
    """Run benchmark with a specific system prompt."""
    original_prompt = agent_module.AGENT_SYSTEM_PROMPT
    agent_module.AGENT_SYSTEM_PROMPT = prompt_text

    try:
        return run_benchmark(
            questions=["How to add CORS?", "Why 422 error?", "What is FastAPI?"],
            runs=1,
        )
    finally:
        agent_module.AGENT_SYSTEM_PROMPT = original_prompt


@pytest.fixture(scope="session")
def v1_scores():
    """Ragas scores with baseline prompt v1."""
    logger.info("Running v1 evaluation...")
    return _run_evaluation_with_prompt(_load_prompt("v1"))


@pytest.fixture(scope="session")
def v2_scores():
    """Ragas scores with candidate prompt v2."""
    logger.info("Running v2 evaluation...")
    return _run_evaluation_with_prompt(_load_prompt("v2"))


@pytest.fixture(scope="session")
def v1_benchmark():
    """Performance stats with baseline prompt v1."""
    return _run_benchmark_with_prompt(_load_prompt("v1"))


@pytest.fixture(scope="session")
def v2_benchmark():
    """Performance stats with candidate prompt v2."""
    return _run_benchmark_with_prompt(_load_prompt("v2"))
