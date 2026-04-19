
def test_embed_text_returns_list(embedding_provider):
    """embed_text should return a plain Python list, not a numpy array."""
    result = embedding_provider.embed_text("test")
    assert isinstance(result, list), f"Expected list, got {type(result)}"


def test_embed_text_dimension(embedding_provider):
    """all-MiniLM-L6-v2 always produces 384-dimensional vectors."""
    result = embedding_provider.embed_text("test")
    assert len(result) == 384, f"Expected 384 dimensions, got {len(result)}"


def test_embed_texts_batch(embedding_provider):
    """embed_texts should handle a batch and return one vector per text."""
    texts = ["hello world", "goodbye world"]
    results = embedding_provider.embed_texts(texts)

    assert isinstance(results, list)
    assert len(results) == 2, f"Expected 2 vectors, got {len(results)}"

    for i, vec in enumerate(results):
        assert isinstance(vec, list), f"Vector {i} is {type(vec)}, expected list"
        assert len(vec) == 384, f"Vector {i} has {len(vec)} dims, expected 384"


def test_embed_text_deterministic(embedding_provider):
    """Same input must always produce the same vector."""
    vec1 = embedding_provider.embed_text("deterministic check")
    vec2 = embedding_provider.embed_text("deterministic check")
    assert vec1 == vec2, "Same input produced different vectors"


def test_different_texts_produce_different_vectors(embedding_provider):
    """Different texts must produce different vectors."""
    vec1 = embedding_provider.embed_text("How to add CORS?")
    vec2 = embedding_provider.embed_text("What is a database?")
    assert vec1 != vec2, "Different texts produced identical vectors"
