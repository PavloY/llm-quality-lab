from app.tools import TOOLS_DESCRIPTION, ToolKit
from app.embeddings import SentenceTransformerProvider


def test_toolkit_has_4_tools(embedding_provider):
    """ToolKit should expose exactly 4 tools."""
    toolkit = ToolKit(embedding_provider=embedding_provider)
    tools = toolkit.get_tools()
    assert len(tools) == 4, f"Expected 4 tools, got {len(tools)}"


def test_tools_description_has_4_entries():
    """Each tool must have a JSON Schema description for the LLM."""
    assert len(TOOLS_DESCRIPTION) == 4, f"Expected 4 descriptions, got {len(TOOLS_DESCRIPTION)}"


def test_tool_names_match(embedding_provider):
    """Names in ToolKit must match names in TOOLS_DESCRIPTION."""
    toolkit = ToolKit(embedding_provider=embedding_provider)
    dict_names = set(toolkit.get_tools().keys())
    desc_names = {item["function"]["name"] for item in TOOLS_DESCRIPTION}
    assert dict_names == desc_names, (
        f"Mismatch!\n  ToolKit keys: {dict_names}\n  TOOLS_DESCRIPTION names: {desc_names}"
    )


def test_each_tool_description_has_required_fields():
    """Each tool description must follow OpenAI function calling format."""
    for i, desc in enumerate(TOOLS_DESCRIPTION):
        assert "type" in desc, f"Description {i} missing 'type'"
        assert desc["type"] == "function", f"Description {i} type is '{desc['type']}'"

        assert "function" in desc, f"Description {i} missing 'function'"
        func = desc["function"]

        assert "name" in func, f"Description {i} function missing 'name'"
        assert isinstance(func["name"], str)

        assert "parameters" in func, f"Description {i} function missing 'parameters'"
        assert isinstance(func["parameters"], dict)


def test_each_tool_is_callable(embedding_provider):
    """Every entry in ToolKit must be a callable."""
    toolkit = ToolKit(embedding_provider=embedding_provider)
    for name, func in toolkit.get_tools().items():
        assert callable(func), f"Tool '{name}' is not callable: {type(func)}"
