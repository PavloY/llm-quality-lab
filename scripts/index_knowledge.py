"""Index knowledge base documents into Qdrant.

Reads all .md files from each knowledge directory, splits them by ## headers,
embeds each chunk, and uploads to separate Qdrant collections.

Collections:
  - fastapi_docs      <- data/knowledge/docs/
  - troubleshooting   <- data/knowledge/troubleshooting/
  - faq               <- data/knowledge/faq/
"""

import sys
import uuid
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from app.chunking import split_by_headers
from app.config import settings
from app.embeddings import SentenceTransformerProvider
from app.schemas import ChunkPayload

VECTOR_DIMENSION = 384

COLLECTIONS = {
    "fastapi_docs": project_root / "data" / "knowledge" / "docs",
    "troubleshooting": project_root / "data" / "knowledge" / "troubleshooting",
    "faq": project_root / "data" / "knowledge" / "faq",
}


def read_markdown_files(docs_dir: Path) -> list[dict[str, str]]:
    """Read all .md files and return list of {filename, content}."""
    files = []
    for md_file in sorted(docs_dir.glob("*.md")):
        content = md_file.read_text(encoding="utf-8")
        files.append({"filename": md_file.name, "content": content})
        print(f"    Read: {md_file.name} ({len(content)} chars)")
    return files




def recreate_collection(client: QdrantClient, collection_name: str) -> None:
    """Delete collection if it exists and create a new one."""
    collections = [c.name for c in client.get_collections().collections]
    if collection_name in collections:
        client.delete_collection(collection_name)
        print(f"    Deleted existing: {collection_name}")

    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=VECTOR_DIMENSION,
            distance=Distance.COSINE,
        ),
    )
    print(f"    Created: {collection_name}")


def index_collection(
    client: QdrantClient,
    collection_name: str,
    docs_dir: Path,
    embedding_provider: SentenceTransformerProvider,
) -> int:
    """Index a single collection. Returns number of indexed chunks."""
    print(f"\n  [{collection_name}] from {docs_dir.relative_to(project_root)}")

    if not docs_dir.exists():
        print(f"    WARNING: Directory not found: {docs_dir}")
        return 0

    files = read_markdown_files(docs_dir)
    if not files:
        print(f"    WARNING: No .md files found")
        return 0

    all_chunks: list[ChunkPayload] = []
    for file_info in files:
        chunks = split_by_headers(file_info["filename"], file_info["content"])
        all_chunks.extend(chunks)
    print(f"    Total chunks: {len(all_chunks)}")

    recreate_collection(client, collection_name)

    texts = [chunk.text for chunk in all_chunks]
    print(f"    Embedding {len(texts)} chunks...")
    vectors = embedding_provider.embed_texts(texts)

    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=vector,
            payload=chunk.model_dump(),
        )
        for chunk, vector in zip(all_chunks, vectors)
    ]

    client.upsert(collection_name=collection_name, points=points)
    print(f"    Uploaded {len(points)} points")

    return len(all_chunks)


def main() -> None:
    """Main indexing pipeline for all knowledge bases."""
    print("=" * 60)
    print("Knowledge Base Indexer (Multi-Collection)")
    print("=" * 60)

    client = QdrantClient(path=settings.qdrant_path)
    embedding_provider = SentenceTransformerProvider()

    total_chunks = 0
    for collection_name, docs_dir in COLLECTIONS.items():
        count = index_collection(client, collection_name, docs_dir, embedding_provider)
        total_chunks += count

    print("\n" + "=" * 60)
    print("Indexing complete!")
    print(f"  Total chunks: {total_chunks}")
    for collection_name in COLLECTIONS:
        info = client.get_collection(collection_name)
        print(f"  {collection_name}: {info.points_count} points")
    print("=" * 60)


if __name__ == "__main__":
    main()
