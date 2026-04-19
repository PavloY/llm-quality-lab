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
