from allure import description


class TestHealthEndpoint:
    """Verify GET /health contract."""

    @description("GET /health returns 200 with {'status': 'ok'}")
    def test_api_01(self, client):
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
