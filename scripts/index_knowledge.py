"""Index knowledge base documents into Qdrant.

Reads all .md files from data/knowledge/docs/, splits them by ## headers,
embeds each chunk, and uploads to a Qdrant collection.
"""

import sys
import uuid
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from app.config import settings
from app.embeddings import SentenceTransformerProvider
from app.schemas import ChunkPayload

COLLECTION_NAME = "fastapi_docs"
VECTOR_DIMENSION = 384
DOCS_DIR = project_root / "data" / "knowledge" / "docs"


def read_markdown_files(docs_dir: Path) -> list[dict[str, str]]:
    """Read all .md files and return list of {filename, content}."""
    files = []
    for md_file in sorted(docs_dir.glob("*.md")):
        content = md_file.read_text(encoding="utf-8")
        files.append({"filename": md_file.name, "content": content})
        print(f"  Read: {md_file.name} ({len(content)} chars)")
    return files


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


def recreate_collection(client: QdrantClient) -> None:
    """Delete collection if it exists and create a new one."""
    collections = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME in collections:
        client.delete_collection(COLLECTION_NAME)
        print(f"  Deleted existing collection: {COLLECTION_NAME}")

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=VECTOR_DIMENSION,
            distance=Distance.COSINE,
        ),
    )
    print(f"  Created collection: {COLLECTION_NAME}")


def index_chunks(
    client: QdrantClient,
    chunks: list[ChunkPayload],
    embedding_provider: SentenceTransformerProvider,
) -> None:
    """Embed chunks and upload to Qdrant."""
    texts = [chunk.text for chunk in chunks]
    print(f"  Embedding {len(texts)} chunks...")
    vectors = embedding_provider.embed_texts(texts)

    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=vector,
            payload=chunk.model_dump(),
        )
        for chunk, vector in zip(chunks, vectors)
    ]

    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"  Uploaded {len(points)} points to Qdrant")


def main() -> None:
    """Main indexing pipeline."""
    print("=" * 60)
    print("Knowledge Base Indexer")
    print("=" * 60)

    print("\n[1/4] Reading markdown files...")
    if not DOCS_DIR.exists():
        print(f"ERROR: Docs directory not found: {DOCS_DIR}")
        sys.exit(1)

    files = read_markdown_files(DOCS_DIR)
    if not files:
        print("ERROR: No .md files found")
        sys.exit(1)
    print(f"  Total files: {len(files)}")

    print("\n[2/4] Splitting into chunks by ## headers...")
    all_chunks: list[ChunkPayload] = []
    for file_info in files:
        chunks = split_by_headers(file_info["filename"], file_info["content"])
        print(f"  {file_info['filename']}: {len(chunks)} chunks")
        all_chunks.extend(chunks)
    print(f"  Total chunks: {len(all_chunks)}")

    print("\n[3/4] Setting up Qdrant collection...")
    client = QdrantClient(path=settings.qdrant_path)
    recreate_collection(client)

    print("\n[4/4] Embedding and indexing...")
    embedding_provider = SentenceTransformerProvider()
    index_chunks(client, all_chunks, embedding_provider)

    collection_info = client.get_collection(COLLECTION_NAME)
    print("\n" + "=" * 60)
    print("Indexing complete!")
    print(f"  Collection: {COLLECTION_NAME}")
    print(f"  Points: {collection_info.points_count}")
    print(f"  Vector size: {collection_info.config.params.vectors.size}")
    print("=" * 60)


if __name__ == "__main__":
    main()
