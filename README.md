# LLM Quality Lab

A RAG + ReAct Agent application built from scratch, covered with **5 levels of testing** — from unit tests to regression detection.

The application is the test subject. **Testing and quality assurance is the core focus.**

## What It Does

A technical support agent for FastAPI documentation. User asks a question → Agent decides which knowledge base to search → retrieves relevant chunks → generates an answer based on context.

```
User: "Why am I getting 422 error?"
  → Agent selects tool: search_troubleshoot
  → Qdrant finds: error_422.md (score: 0.72)
  → GPT generates answer from retrieved context
  → Response with sources and reasoning steps
```

## Architecture

```
FastAPI (POST /query)
    → Agent (ReAct: think → act → observe)
        → ToolKit (4 tools: search_docs, search_troubleshoot, search_faq, no_search_needed)
            → QdrantRetriever (embed query → vector search → results)
                → SentenceTransformer (all-MiniLM-L6-v2, dim=384)
                → Qdrant (local, 3 collections, 72 chunks)
```

## Testing Pyramid (67 tests)

| Level | Tests | What it catches |
|-------|-------|----------------|
| **Unit** | 30 | Broken components (embeddings, schemas, chunking, tools) |
| **Integration** | 11 | Broken interactions (retrieval relevance, API contract) |
| **Observability** | 5 | Missing/broken logs, timing |
| **Quality (Ragas)** | 9 | Hallucinations, irrelevant answers, bad retrieval |
| **Safety** | 7 | Prompt injection, PII leakage, toxicity |
| **Performance** | 5 | Latency SLA violations (p95 < 10s) |
| **Regression** | 5 | Quality degradation after prompt/model changes |

## Tech Stack

- **Python 3.11+** / FastAPI / Pydantic v2
- **Qdrant**
- **sentence-transformers**
- **OpenAI API**
- **pytest** + allure-pytest + ruff
- **Ragas**

## Project Structure

```
app/                    — Application code (agent, RAG, tools, API)
data/                   — Knowledge bases, golden examples, canary prompts
tests/
├── unit/               — 30 tests (embeddings, schemas, chunking, tools)
├── integration/        — 11 tests (retrieval, API contract)
├── observability/      — 5 tests (structured logging)
├── quality/            — 9 tests (Ragas: faithfulness, relevancy, recall)
├── safety/             — 7 tests (injection, PII, toxicity, prompt leakage)
├── performance/        — 5 tests (latency SLA, step count)
└── regression/         — 5 tests (prompt v1 vs v2 comparison)
configs/                — Prompt versions, eval config
scripts/                — Indexer, benchmark, test runner
```

## Quick Start

```bash
# Install
python -m venv .venv && source .venv/Scripts/activate
pip install -r requirements.txt

# Index knowledge base
python scripts/index_knowledge.py

# Run fast tests (free, 2s)
bash scripts/run_tests.sh fast

# Run all levels
bash scripts/run_tests.sh full
```

## Key Design Decisions

- **OOP + SOLID**: Protocol-based interfaces, dependency injection, composition over inheritance
- **1 test file = 1 test class**: clean separation, easy navigation
- **Allure @description + TC IDs**: traceability between test design and code
- **LoggingRetriever / LoggingClient**: transparent logging via Decorator pattern
- **iterate_canary()**: allure.step under the hood, tests stay pure assertions
- **Session-scoped fixtures**: expensive operations (model loading, Ragas eval) run once
