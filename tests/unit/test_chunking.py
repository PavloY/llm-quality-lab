from app.chunking import split_by_headers


SAMPLE_MARKDOWN = """# Main Title

Some introduction text before any ## header.

## First Section

Content of the first section.
More content here.

## Second Section

Content of the second section.

## Third Section

Content of the third section.
Even more content.
"""


def test_chunks_from_markdown():
    """Markdown with 3 ## headers should produce 4 chunks (intro + 3 sections)."""
    chunks = split_by_headers("test.md", SAMPLE_MARKDOWN)
    assert len(chunks) == 4, f"Expected 4 chunks, got {len(chunks)}"


def test_chunk_has_required_fields():
    """Each chunk must have non-empty text, header, and source."""
    chunks = split_by_headers("test.md", SAMPLE_MARKDOWN)

    for i, chunk in enumerate(chunks):
        assert chunk.text.strip(), f"Chunk {i} has empty text"
        assert chunk.header.strip(), f"Chunk {i} has empty header"
        assert chunk.source == "test.md", f"Chunk {i} source is '{chunk.source}'"


def test_chunk_headers_are_correct():
    """Headers should be extracted from ## lines."""
    chunks = split_by_headers("test.md", SAMPLE_MARKDOWN)
    headers = [c.header for c in chunks]

    assert headers[0] == "Introduction"
    assert "First Section" in headers
    assert "Second Section" in headers
    assert "Third Section" in headers


def test_empty_document():
    """Empty document should return empty list."""
    chunks = split_by_headers("empty.md", "")
    assert chunks == [], f"Expected empty list, got {chunks}"


def test_document_without_headers():
    """Document with no ## headers should return one chunk with 'Introduction' header."""
    content = "Just some text\nwithout any headers\nat all."
    chunks = split_by_headers("no_headers.md", content)

    assert len(chunks) == 1
    assert chunks[0].header == "Introduction"
    assert "Just some text" in chunks[0].text


def test_source_propagates():
    """The source filename should propagate to every chunk."""
    chunks = split_by_headers("middleware.md", SAMPLE_MARKDOWN)
    for chunk in chunks:
        assert chunk.source == "middleware.md"
