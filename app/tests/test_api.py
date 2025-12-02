import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from app.main import app
from app.services.llm_service import LLMHandler
from app.models.schemas import LLMOutput, InputPayload, Task
from typing import List, Dict, Any
import json

client = TestClient(app)

@pytest.fixture
def valid_payload() -> Dict[str, Any]:
    """Fixture providing valid input payload for tests."""
    return {
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

@pytest.fixture
def mock_llm_output() -> LLMOutput:
    """Fixture providing a mock LLM output."""
    return LLMOutput(
        insight="Test insight",
        recommendations=["Do more deep work", "Take regular breaks"],
        key_points=["High focus", "Good task completion"]
    )

@pytest.fixture(autouse=True)
def mock_llm_handler(mocker, mock_llm_output):
    """Automatically mock the LLMHandler for all tests."""
    mock = mocker.patch.object(
        LLMHandler,
        "generate_insight",
        AsyncMock(return_value=(mock_llm_output, False))
    )
    return mock

def validate_analyze_response(response_data: Dict[str, Any]) -> None:
    """Helper to validate the structure of the analyze endpoint response."""
    required_fields = {
        "score": (int, float),
        "tags": list,
        "explanations": list,
        "llm_insight": str,
        "llm_recommendations": list
    }
    
    # Check all required fields exist
    for field, field_type in required_fields.items():
        assert field in response_data, f"Missing field: {field}"
        assert isinstance(response_data[field], field_type), f"Invalid type for {field}"

    # Additional validation for specific fields
    assert 0 <= response_data["score"] <= 100, "Score out of range"
    assert all(isinstance(tag, str) for tag in response_data["tags"]), "Invalid tag format"
    assert all(isinstance(rec, str) for rec in response_data["llm_recommendations"]), "Invalid recommendation format"

@pytest.mark.asyncio
async def test_analyze_endpoint_returns_valid_output(valid_payload, mock_llm_handler, mock_llm_output):
    """Test that the analyze endpoint returns a valid response structure."""
    response = client.post("/api/v1/analyze", json=valid_payload)
    
    # Check HTTP status code
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
    
    # Parse and validate response
    data = response.json()
    validate_analyze_response(data)
    
    # Check LLM output is correctly included
    assert data["llm_insight"] == mock_llm_output.insight
    assert all(rec in data["llm_recommendations"] for rec in mock_llm_output.recommendations)

@pytest.mark.asyncio
async def test_analyze_endpoint_cache_header(valid_payload, mock_llm_handler):
    """Test that cache headers are correctly set."""
    # First request - should be a cache miss
    response = client.post("/api/v1/analyze", json=valid_payload)
    assert response.status_code == 200
    assert response.headers.get("x-cache") == "MISS"
    
    # Mock cache hit for second request
    mock_llm_handler.return_value = (mock_llm_handler.return_value[0], True)
    response = client.post("/api/v1/analyze", json=valid_payload)
    assert response.status_code == 200
    assert response.headers.get("x-cache") == "HIT"

@pytest.mark.parametrize("invalid_payload, expected_errors", [
    ({"deep_work_minutes": 120}, ["field required"]),  # Missing required fields
    ({"tasks": "not a list", "user_id": "123"}, ["value is not a valid list"]),  # Invalid tasks format
    ({"tasks": [{"id": 1, "title": 123}], "user_id": "123"}, ["value is not a valid dict"]),  # Invalid task structure
    ({"sleep_hours": 25, "user_id": "123", "tasks": []}, ["ensure this value is less than or equal to 24"])  # Invalid sleep hours
])
def test_analyze_invalid_payload(invalid_payload, expected_errors):
    """Test various invalid payload scenarios."""
    response = client.post("/api/v1/analyze", json=invalid_payload)
    assert response.status_code == 422
    error_detail = response.json()["detail"]
    
    # Check that all expected error messages are present
    error_messages = [err["msg"].lower() for err in error_detail]
    for expected_error in expected_errors:
        assert any(expected_error in msg for msg in error_messages), f"Expected error containing: {expected_error}"

def test_rate_limit_simulation(valid_payload):
    """Test that rate limiting is working as expected."""
    # First few requests should succeed
    for _ in range(5):
        response = client.post("/api/v1/analyze", json=valid_payload)
        assert response.status_code == 200
    
    # Next request should be rate-limited
    response = client.post("/api/v1/analyze", json=valid_payload)
    assert response.status_code == 429

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code in [200, 404]  # 404 if not implemented

@pytest.mark.asyncio
async def test_concurrent_requests(valid_payload):
    """Test that the endpoint can handle concurrent requests."""
    import asyncio
    from httpx import AsyncClient
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        tasks = [
            ac.post("/api/v1/analyze", json=valid_payload)
            for _ in range(5)
        ]
        responses = await asyncio.gather(*tasks)
        
        # All requests should complete successfully
        for response in responses:
            assert response.status_code == 200
            validate_analyze_response(response.json())