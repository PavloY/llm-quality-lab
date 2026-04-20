from allure import description

from app.tools import TOOLS_DESCRIPTION


class TestToolsFormat:
    """Verify ToolKit and TOOLS_DESCRIPTION are consistent and correctly formatted."""

    @description("ToolKit exposes exactly 4 tools")
    def test_tls_01(self, toolkit):
        tools = toolkit.get_tools()

        assert len(tools) == 4, f"Expected 4 tools, got {len(tools)}"

    @description("TOOLS_DESCRIPTION has one entry per tool")
    def test_tls_02(self):
        assert len(TOOLS_DESCRIPTION) == 4, f"Expected 4, got {len(TOOLS_DESCRIPTION)}"

    @description("Names in ToolKit match names in TOOLS_DESCRIPTION")
    def test_tls_03(self, toolkit):
        dict_names = set(toolkit.get_tools().keys())
        desc_names = {item["function"]["name"] for item in TOOLS_DESCRIPTION}

        assert dict_names == desc_names, (
            f"Mismatch!\n  ToolKit: {dict_names}\n  Description: {desc_names}"
        )

    @description("Each description follows OpenAI function calling schema")
    def test_tls_04(self):
        for i, desc in enumerate(TOOLS_DESCRIPTION):
            assert desc.get("type") == "function", f"Desc {i}: type != 'function'"

            func = desc.get("function", {})
            assert isinstance(func.get("name"), str), f"Desc {i}: missing name"
            assert isinstance(func.get("parameters"), dict), f"Desc {i}: missing parameters"

    @description("Every tool in ToolKit is callable")
    def test_tls_05(self, toolkit):
        for name, func in toolkit.get_tools().items():
            assert callable(func), f"Tool '{name}' is not callable: {type(func)}"
