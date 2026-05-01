from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ChunkPayload(BaseModel):
    """A chunk of text extracted from a knowledge base document."""

    text: str
    source: str = Field(description="Source filename")
    header: str = Field(description="Section header within the document")


class RetrievalResult(BaseModel):
    """A single result from vector similarity search."""

    text: str
    source: str
    score: float = Field(ge=0.0, le=1.0)


class RAGResponse(BaseModel):
    """Complete response from the RAG pipeline."""

    answer: str
    sources: list[str] = Field(description="Source filenames used for the answer")
    chunks_used: int = Field(ge=0)
    route: "QueryRoute | None" = Field(default=None, description="Routing decision if routed")


class QueryRoute(BaseModel):
    """SGR Routing: classify which knowledge base to search."""

    intent: Literal["docs", "troubleshooting", "faq"] = Field(
        description="Which knowledge base is most relevant"
    )
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str = Field(description="Brief explanation of why this KB was chosen")


class AgentStep(BaseModel):
    """One step of the ReAct cycle."""

    thought: str = Field(description="Agent's reasoning about what to do")
    action: str = Field(description="Tool name to call")
    action_input: dict = Field(default_factory=dict, description="Arguments for the tool")
    observation: str | None = Field(default=None, description="Result from tool execution")


class AgentResponse(BaseModel):
    """Complete agent response with reasoning trace."""

    steps: list[AgentStep] = Field(description="ReAct reasoning steps")
    final_answer: str = Field(description="Final answer to the user")
    sources: list[str] = Field(default_factory=list, description="Source documents used")
    total_steps: int = Field(ge=0, description="Number of reasoning steps taken")
    tools_used: list[str] = Field(default_factory=list, description="Tools that were called")


class ToolCall(BaseModel):
    """Provider-neutral representation of a tool invocation requested by the LLM."""

    id: str = Field(description="Unique ID linking this call to its result")
    name: str = Field(description="Tool name")
    arguments: dict = Field(default_factory=dict, description="Parsed JSON arguments")


class AssistantMessage(BaseModel):
    """Provider-neutral assistant response message."""

    content: str | None = Field(default=None, description="Text content, None if only tool calls")
    tool_calls: list[ToolCall] = Field(default_factory=list)


class LLMToolResponse(BaseModel):
    """Unified return type for LLMProvider.generate_with_tools()."""

    message: AssistantMessage
    stop_reason: Literal["tool_use", "end_turn", "max_tokens", "stop", "other"] = Field(
        description="Normalized stop reason across providers"
    )
    tokens_in: int = Field(default=0, ge=0)
    tokens_out: int = Field(default=0, ge=0)
