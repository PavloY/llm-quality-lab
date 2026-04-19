from fastapi import FastAPI
from pydantic import BaseModel

from app.agent import Agent
from app.embeddings import SentenceTransformerProvider
from app.llm import OpenAIProvider
from app.schemas import AgentResponse
from app.tools import ToolKit

app = FastAPI(title="Tech Knowledge Agent", version="0.1.0")

_provider = SentenceTransformerProvider()
_llm = OpenAIProvider()
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
