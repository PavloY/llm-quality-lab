from fastapi import FastAPI
from pydantic import BaseModel

from app.agent import Agent
from app.embeddings import SentenceTransformerProvider
from app.llm_factory import get_llm
from app.logging_config import setup_logging
from app.schemas import AgentResponse
from app.tools import ToolKit

setup_logging()

app = FastAPI(title="Tech Knowledge Agent", version="0.1.0")

_provider = SentenceTransformerProvider()
_llm = get_llm("main")
_toolkit = ToolKit(embedding_provider=_provider)


class QueryRequest(BaseModel):
    question: str


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/query", response_model=AgentResponse)
def query(request: QueryRequest):
    """Send a question to the agent and get a structured response."""
    agent = Agent(toolkit=_toolkit, llm_provider=_llm)
    return agent.query(request.question)
