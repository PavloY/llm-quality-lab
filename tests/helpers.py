from app.schemas import RetrievalResult


def assert_results_contain(results: list[RetrievalResult], keyword: str) -> None:
    """Assert that at least one result's text contains the keyword."""
    texts = " ".join(r.text.lower() for r in results)
    assert keyword.lower() in texts, (
        f"'{keyword}' not found in results. Sources: {[r.source for r in results]}"
    )
