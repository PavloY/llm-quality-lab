from allure import description


class TestQueryEndpoint:
    """Verify POST /query contract with mocked Agent."""

    @description("POST /query with valid question returns 200")
    def test_api_02(self, client, mock_agent):
        response = client.post("/query", json={"question": "How to add CORS?"})

        assert response.status_code == 200

    @description("Response contains all AgentResponse fields with correct values")
    def test_api_03(self, client, mock_agent):
        response = client.post("/query", json={"question": "test"})

        data = response.json()
        assert "steps" in data
        assert "final_answer" in data
        assert "sources" in data
        assert "total_steps" in data
        assert "tools_used" in data
        assert data["final_answer"] == "Here is a test answer based on the docs."
        assert data["total_steps"] == 1
        assert "search_docs" in data["tools_used"]
        assert "test_doc.md" in data["sources"]

    @description("POST /query without body returns 422 validation error")
    def test_api_04(self, client):
        response = client.post("/query")

        assert response.status_code == 422

    @description("POST /query with wrong field name returns 422")
    def test_api_05(self, client):
        response = client.post("/query", json={"wrong_field": "test"})

        assert response.status_code == 422
