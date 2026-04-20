from allure import description


class TestEmbeddings:
    """Verify that SentenceTransformerProvider produces correct vectors."""

    @description("embed_text returns plain Python list, not numpy array")
    def test_emb_01(self, embedding_provider):
        result = embedding_provider.embed_text("test")

        assert isinstance(result, list), f"Expected list, got {type(result)}"

    @description("all-MiniLM-L6-v2 produces 384-dimensional vectors")
    def test_emb_02(self, embedding_provider):
        result = embedding_provider.embed_text("test")

        assert len(result) == 384, f"Expected 384, got {len(result)}"

    @description("embed_texts batch: 2 texts → 2 vectors of 384 each")
    def test_emb_03(self, embedding_provider):
        texts = ["hello world", "goodbye world"]

        results = embedding_provider.embed_texts(texts)

        assert len(results) == 2, f"Expected 2 vectors, got {len(results)}"
        for i, vec in enumerate(results):
            assert isinstance(vec, list), f"Vector {i} is {type(vec)}"
            assert len(vec) == 384, f"Vector {i} has {len(vec)} dims"

    @description("Same input always produces the same vector (deterministic)")
    def test_emb_04(self, embedding_provider):
        vec1 = embedding_provider.embed_text("deterministic check")
        vec2 = embedding_provider.embed_text("deterministic check")

        assert vec1 == vec2, "Same input produced different vectors"

    @description("Different texts produce different vectors")
    def test_emb_05(self, embedding_provider):
        vec1 = embedding_provider.embed_text("How to add CORS?")
        vec2 = embedding_provider.embed_text("What is a database?")

        assert vec1 != vec2, "Different texts produced identical vectors"
