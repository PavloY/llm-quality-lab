from allure import description

from app.chunking import split_by_headers
from tests.test_data import SAMPLE_MARKDOWN


class TestChunking:
    """Verify split_by_headers splits markdown correctly by ## headers."""

    @description("3 headers ## → 4 chunks (intro + 3 sections)")
    def test_chk_01(self):
        chunks = split_by_headers("test.md", SAMPLE_MARKDOWN)

        assert len(chunks) == 4, f"Expected 4 chunks, got {len(chunks)}"

    @description("Each chunk has non-empty text, header, and correct source")
    def test_chk_02(self):
        chunks = split_by_headers("test.md", SAMPLE_MARKDOWN)

        for i, chunk in enumerate(chunks):
            assert chunk.text.strip(), f"Chunk {i} has empty text"
            assert chunk.header.strip(), f"Chunk {i} has empty header"
            assert chunk.source == "test.md", f"Chunk {i} source is '{chunk.source}'"

    @description("First header is 'Introduction', rest extracted from ## lines")
    def test_chk_03(self):
        chunks = split_by_headers("test.md", SAMPLE_MARKDOWN)
        headers = [c.header for c in chunks]

        assert headers[0] == "Introduction"
        assert "First Section" in headers
        assert "Second Section" in headers
        assert "Third Section" in headers

    @description("Empty document returns empty list")
    def test_chk_04(self):
        chunks = split_by_headers("empty.md", "")

        assert chunks == []

    @description("Document without ## returns one chunk with 'Introduction' header")
    def test_chk_05(self):
        content = "Just some text\nwithout any headers\nat all."

        chunks = split_by_headers("no_headers.md", content)

        assert len(chunks) == 1
        assert chunks[0].header == "Introduction"
        assert "Just some text" in chunks[0].text

    @description("Source filename propagates to every chunk")
    def test_chk_06(self):
        chunks = split_by_headers("middleware.md", SAMPLE_MARKDOWN)

        for chunk in chunks:
            assert chunk.source == "middleware.md"
