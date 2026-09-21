from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "app": "R & A Agent"}


def test_chat_endpoint_success() -> None:
    mock_workflow_result = {
        "user_input": "What is 2 + 2?",
        "research": "Calculated 2 + 2 = 4",
        "final_answer": "The sum of 2 and 2 is 4.",
        "tool_calls": 1,
    }

    with patch("app.api.routes.chat.workflow.invoke", return_value=mock_workflow_result):
        response = client.post("/api/v1/chat", json={"message": "What is 2 + 2?"})
        assert response.status_code == 200
        data = response.json()
        assert data["answer"] == "The sum of 2 and 2 is 4."
        assert data["tool_calls"] == 1


def test_chat_endpoint_empty_message_validation() -> None:
    response = client.post("/api/v1/chat", json={"message": ""})
    assert response.status_code == 422


def test_chat_endpoint_oversized_message_validation() -> None:
    oversized = "a" * 1001
    response = client.post("/api/v1/chat", json={"message": oversized})
    assert response.status_code == 422


def test_chat_endpoint_internal_error_handling() -> None:
    with patch("app.api.routes.chat.workflow.invoke", side_effect=Exception("Database failure")):
        response = client.post("/api/v1/chat", json={"message": "Valid query"})
        assert response.status_code == 500
        assert "Workflow execution failed" in response.json()["detail"]
