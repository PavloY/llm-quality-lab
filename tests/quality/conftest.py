import json
import logging

import pytest
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import answer_relevancy, context_recall, faithfulness

from app.agent import Agent
from app.embeddings import SentenceTransformerProvider
from app.llm import OpenAIProvider
from app.tools import ToolKit

logger = logging.getLogger("tests.quality")

GOLDEN_PATH = "data/golden_examples.json"
GOLDEN_QUICK_PATH = "data/golden_examples_quick.json"


@pytest.fixture(scope="session")
def golden_examples():
    with open(GOLDEN_PATH) as f:
        return json.load(f)


@pytest.fixture(scope="session")
def golden_examples_quick():
    with open(GOLDEN_QUICK_PATH) as f:
        return json.load(f)


def _run_agent_on_examples(examples: list[dict]) -> Dataset:
    """Run agent on each example and build Ragas-compatible dataset.

    Skips out_of_scope examples (no ground truth for Ragas).
    """
    provider = SentenceTransformerProvider()
    llm = OpenAIProvider()
    toolkit = ToolKit(embedding_provider=provider)

    questions = []
    answers = []
    contexts = []
    ground_truths = []

    filtered = [ex for ex in examples if ex.get("category") != "out_of_scope"]
    logger.info("Running agent on %d examples (skipped %d out_of_scope)", len(filtered), len(examples) - len(filtered))

    for i, ex in enumerate(filtered):
        logger.info("  [%d/%d] %s", i + 1, len(filtered), ex["question"][:60])

        agent = Agent(toolkit=toolkit, llm_provider=llm)
        result = agent.query(ex["question"])

        ctx = [step.observation for step in result.steps if step.observation]

        questions.append(ex["question"])
        answers.append(result.final_answer)
        contexts.append(ctx if ctx else ["No context retrieved"])
        ground_truths.append(ex["ground_truth"])

    logger.info("Agent run complete. Building Ragas dataset...")

    return Dataset.from_dict({
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": ground_truths,
    })


@pytest.fixture(scope="session")
def ragas_result(golden_examples):
    """Full Ragas evaluation (~22 examples, ~15 min)."""
    logger.info("Starting full Ragas evaluation...")
    dataset = _run_agent_on_examples(golden_examples)
    result = evaluate(dataset, metrics=[faithfulness, answer_relevancy, context_recall])
    logger.info("Full Ragas result: %s", dict(result))
    return result


@pytest.fixture(scope="session")
def ragas_result_quick(golden_examples_quick):
    """Quick Ragas evaluation (5 examples, ~3 min)."""
    logger.info("Starting quick Ragas evaluation...")
    dataset = _run_agent_on_examples(golden_examples_quick)
    result = evaluate(dataset, metrics=[faithfulness, answer_relevancy, context_recall])
    logger.info("Quick Ragas result: %s", dict(result))
    return result


@pytest.fixture(scope="session")
def ragas_per_category(golden_examples):
    """Per-category Ragas evaluation for breakdown analysis."""
    categories = sorted(set(
        ex["category"] for ex in golden_examples
        if ex.get("category") != "out_of_scope"
    ))
    logger.info("Running per-category evaluation for: %s", categories)

    results = {}
    for cat in categories:
        cat_examples = [ex for ex in golden_examples if ex.get("category") == cat]
        logger.info("  Category '%s': %d examples", cat, len(cat_examples))
        dataset = _run_agent_on_examples(cat_examples)
        result = evaluate(dataset, metrics=[faithfulness, answer_relevancy, context_recall])
        results[cat] = dict(result)
        logger.info("  %s: %s", cat, results[cat])

    return results
