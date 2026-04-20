import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "scripts"))

from benchmark import run_benchmark

PERF_QUESTIONS = [
    "How to add CORS in FastAPI?",
    "Why am I getting 422 validation error?",
    "What is FastAPI?",
]


@pytest.fixture(scope="session")
def benchmark():
    """Run benchmark once for all performance tests (3 questions)."""
    return run_benchmark(questions=PERF_QUESTIONS, runs=1)
