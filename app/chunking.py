from app.schemas import ChunkPayload


def split_by_headers(filename: str, content: str) -> list[ChunkPayload]:
    """Split markdown content by ## headers into typed chunks."""
    chunks: list[ChunkPayload] = []
    current_header = "Introduction"
    current_lines: list[str] = []

    for line in content.split("\n"):
        if line.startswith("## "):
            chunk_text = "\n".join(current_lines).strip()
            if chunk_text:
                chunks.append(ChunkPayload(
                    text=chunk_text,
                    source=filename,
                    header=current_header,
                ))
            current_header = line.lstrip("# ").strip()
            current_lines = [line]
        else:
            current_lines.append(line)

    chunk_text = "\n".join(current_lines).strip()
    if chunk_text:
        chunks.append(ChunkPayload(
            text=chunk_text,
            source=filename,
            header=current_header,
        ))

    return chunks
