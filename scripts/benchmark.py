import json
import statistics
import sys
import time
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from app.agent import Agent
from app.embeddings import SentenceTransformerProvider
from app.llm import OpenAIProvider
from app.tools import ToolKit

BENCHMARK_QUESTIONS = [
    "How to add CORS in FastAPI?",
    "Why am I getting 422 validation error?",
    "What is dependency injection?",
    "How to handle errors in FastAPI?",
    "What is FastAPI?",
    "How to test FastAPI apps?",
    "My app is slow, what to do?",
    "How to add JWT authentication?",
    "Async vs sync in FastAPI?",
    "How to deploy with Docker?",
]


def run_benchmark(questions: list[str] | None = None, runs: int = 1) -> dict:
    """Run agent on questions and collect performance stats."""
    questions = questions or BENCHMARK_QUESTIONS

    provider = SentenceTransformerProvider()
    llm = OpenAIProvider()
    toolkit = ToolKit(embedding_provider=provider)

    all_results = []

    for q in questions * runs:
        agent = Agent(toolkit=toolkit, llm_provider=llm)
        start = time.perf_counter()
        result = agent.query(q)
        total = time.perf_counter() - start

        all_results.append({
            "question": q[:50],
            "total_seconds": round(total, 2),
            "steps": result.total_steps,
            "tools_used": result.tools_used,
        })

    totals = [r["total_seconds"] for r in all_results]
    steps = [r["steps"] for r in all_results]

    return {
        "total_requests": len(all_results),
        "total_p50": round(statistics.median(totals), 2),
        "total_p95": round(sorted(totals)[int(len(totals) * 0.95)] if len(totals) >= 2 else max(totals), 2),
        "total_mean": round(statistics.mean(totals), 2),
        "total_max": round(max(totals), 2),
        "avg_steps": round(statistics.mean(steps), 1),
        "max_steps": max(steps),
    }


def save_benchmark(stats: dict, label: str = "baseline") -> None:
    """Save benchmark results to reports/ directory."""
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    path = reports_dir / f"benchmark_{label}.json"
    with open(path, "w") as f:
        json.dump(stats, f, indent=2)
    print(f"Saved to {path}")


if __name__ == "__main__":
    label = sys.argv[1] if len(sys.argv) > 1 else "baseline"
    print(f"Running benchmark ({label})...")
    stats = run_benchmark()
    save_benchmark(stats, label)
    print(json.dumps(stats, indent=2))
