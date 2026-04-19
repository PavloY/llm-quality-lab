from unittest.mock import patch, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas import AgentResponse, AgentStep


@pytest.fixture
def client():
    """FastAPI TestClient."""
    return TestClient(app)


MOCK_AGENT_RESPONSE = AgentResponse(
    steps=[
        AgentStep(
            thought="I need to search the docs",
            action="search_docs",
            action_input={"query": "test"},
            observation="Found some docs about testing",
        ),
    ],
    final_answer="Here is a test answer based on the docs.",
    sources=["test_doc.md"],
    total_steps=1,
    tools_used=["search_docs"],
)


def test_health_endpoint(client):
    """GET /health should always return 200 with status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_query_endpoint_returns_200(client):
    """POST /query with a valid question should return 200."""
    with patch("app.main.Agent") as MockAgent:
        mock_instance = MagicMock()
        mock_instance.query.return_value = MOCK_AGENT_RESPONSE
        MockAgent.return_value = mock_instance

        response = client.post("/query", json={"question": "How to add CORS?"})

    assert response.status_code == 200


def test_query_response_has_required_fields(client):
    """POST /query response must contain all AgentResponse fields."""
    with patch("app.main.Agent") as MockAgent:
        mock_instance = MagicMock()
        mock_instance.query.return_value = MOCK_AGENT_RESPONSE
        MockAgent.return_value = mock_instance

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


def test_query_without_body_returns_422(client):
    """POST /query without JSON body should return 422 validation error."""
    response = client.post("/query")
    assert response.status_code == 422


def test_query_with_empty_question_returns_422(client):
    """POST /query with invalid body format should return 422."""
    response = client.post("/query", json={"wrong_field": "test"})
    assert response.status_code == 422
