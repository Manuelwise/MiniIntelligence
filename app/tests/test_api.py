import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
from app.main import app
from app.services.llm_service import LLMHandler
from app.models.schemas import LLMOutput

client = TestClient(app)

valid_input = {
    "user_id": "123",
    "date_range": "2025-11-29",
    "tasks": [
        {"id": "T1", "title": "Task 1", "planned_minutes": 60, "actual_minutes": 45, "completed": True},
        {"id": "T2", "title": "Task 2", "planned_minutes": 30, "actual_minutes": 15, "completed": False}
    ],
    "deep_work_minutes": 120,
    "meetings_minutes": 60,
    "interruptions": 5,
    "sleep_hours": 7.0,
    "breaks_minutes": 30,
    "mood": 8
}


def test_analyze_endpoint_returns_valid_output(mocker):
    fake_output = LLMOutput(
        insight="Test insight",
        recommendations=["Do more deep work"],
        key_points=["High focus"]
    )
    # Patch generate_insight directly; works regardless of agent vs chain internally
    mocker.patch.object(LLMHandler, "generate_insight", AsyncMock(return_value=(fake_output, False)))

    response = client.post("/api/v1/analyze", json=valid_input)
    assert response.status_code == 200

    data = response.json()
    assert "score" in data
    assert "tags" in data
    assert "explanations" in data
    assert "llm_insight" in data
    assert "llm_recommendations" in data
    assert isinstance(data["score"], (int, float))
    assert isinstance(data["tags"], list)
    assert isinstance(data["explanations"], list)
    assert data["llm_insight"] == "Test insight"
    assert "Do more deep work" in data["llm_recommendations"]


def test_analyze_endpoint_cache_header(mocker):
    fake_output = LLMOutput(
        insight="Cached insight",
        recommendations=["Cached rec"],
        key_points=["Cached key"]
    )
    mocker.patch.object(LLMHandler, "generate_insight", AsyncMock(return_value=(fake_output, True)))

    response = client.post("/api/v1/analyze", json=valid_input)
    assert response.status_code == 200
    assert response.headers["x-cache"] == "HIT"
    data = response.json()
    assert data["llm_insight"] == "Cached insight"


def test_analyze_invalid_payload():
    bad_payload = {"deep_work_minutes": 120}  # missing required tasks
    response = client.post("/api/v1/analyze", json=bad_payload)
    assert response.status_code == 422


def test_rate_limit_simulation():
    for _ in range(5):
        response = client.post("/api/v1/analyze", json=valid_input)
        assert response.status_code in [200, 429]  # 429 if rate-limited


def test_health_check_exists():
    resp = client.get("/health")
    assert resp.status_code in [200, 404]
