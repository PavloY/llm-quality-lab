import pytest
from allure import description
from pydantic import ValidationError

from app.schemas import ChunkPayload


class TestChunkPayload:
    """Verify ChunkPayload validation rules."""

    @description("ChunkPayload accepts all required fields")
    def test_sch_01(self):
        chunk = ChunkPayload(text="some text", source="test.md", header="Intro")

        assert chunk.text == "some text"
        assert chunk.source == "test.md"
        assert chunk.header == "Intro"

    @description("ChunkPayload rejects missing source and header")
    def test_sch_02(self):
        with pytest.raises(ValidationError):
            ChunkPayload(text="some text")
