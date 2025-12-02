import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.llm_service import LLMHandler
from app.models.schemas import RuleExplanation, LLMOutput
from app.config import get_settings
import asyncio

settings = get_settings()

@pytest.fixture
def mock_llm():
    """Fixture to provide a mocked LLMHandler instance with mocked dependencies."""
    with patch('app.services.llm_service.ChatOpenAI') as mock_chat, \
         patch('app.services.llm_service.cache') as mock_cache:
        
        # Setup mock LLM
        mock_llm = MagicMock()
        mock_chat.return_value = mock_llm
        
        # Setup mock cache
        mock_cache.get = AsyncMock(return_value=None)
        mock_cache.set = AsyncMock()
        
        # Create handler with mocks
        handler = LLMHandler()
        handler.llm = mock_llm
        handler.cache = mock_cache
        
        # Mock the agent executor
        mock_agent = AsyncMock()
        mock_agent.ainvoke = AsyncMock(return_value={"output": json.dumps({
            "insight": "Test insight",
            "recommendations": ["Test recommendation"],
            "key_points": ["Test point"]
        })})
        handler.agent_executor = mock_agent
        
        yield handler, mock_agent, mock_cache

@pytest.fixture
def sample_inputs():
    """Fixture providing sample input data for tests."""
    return {
        "score": 85.5,
        "tags": ["focused", "productive"],
        "explanations": [
            RuleExplanation(
                rule_id="deep_work",
                description="Completed 4 hours of deep work",
                effect_on_score=20
            )
        ]
    }

@pytest.mark.asyncio
async def test_generate_insight_success(mock_llm, sample_inputs):
    """Test successful insight generation with valid inputs."""
    handler, mock_agent, _ = mock_llm
    
    # Call the method
    result, from_cache = await handler.generate_insight(**sample_inputs)
    
    # Assertions
    assert isinstance(result, LLMOutput)
    assert result.insight == "Test insight"
    assert len(result.recommendations) == 1
    assert not from_cache
    mock_agent.ainvoke.assert_called_once()

@pytest.mark.asyncio
async def test_generate_insight_caching(mock_llm, sample_inputs):
    """Test that caching works as expected."""
    handler, mock_agent, mock_cache = mock_llm
    
    # Setup cache hit
    cached_output = {
        "insight": "Cached insight",
        "recommendations": ["Cached rec"],
        "key_points": ["Cached point"]
    }
    mock_cache.get = AsyncMock(return_value=cached_output)
    
    result, from_cache = await handler.generate_insight(**sample_inputs)
    
    assert from_cache is True
    assert result.insight == "Cached insight"
    mock_agent.ainvoke.assert_not_called()  # Should use cache

@pytest.mark.asyncio
async def test_generate_insight_error_handling(mock_llm, sample_inputs):
    """Test error handling in insight generation."""
    handler, mock_agent, _ = mock_llm
    mock_agent.ainvoke.side_effect = Exception("API Error")
    
    result, from_cache = await handler.generate_insight(**sample_inputs)
    
    assert "error" in result.insight.lower()
    assert not from_cache

@pytest.mark.asyncio
async def test_generate_insight_invalid_json_response(mock_llm, sample_inputs):
    """Test handling of invalid JSON response from LLM."""
    handler, mock_agent, _ = mock_llm
    mock_agent.ainvoke.return_value = {"output": "This is not valid JSON"}
    
    result, from_cache = await handler.generate_insight(**sample_inputs)
    
    assert "AI error" in result.insight
    assert not from_cache

def test_llm_handler_initialization():
    """Test LLMHandler initialization with custom parameters."""
    test_model = "test-model"
    test_temp = 0.8
    
    with patch('app.services.llm_service.ChatOpenAI') as mock_chat:
        handler = LLMHandler(model_name=test_model, temperature=test_temp)
        
        # Assert ChatOpenAI was initialized with correct parameters
        mock_chat.assert_called_once_with(
            model=test_model,
            temperature=test_temp,
            openai_api_key=settings.LLM_API_KEY
        )

@pytest.mark.asyncio
async def test_concurrent_requests(mock_llm, sample_inputs):
    """Test that the handler can handle concurrent requests."""
    handler, mock_agent, _ = mock_llm
    
    # Create multiple concurrent requests
    tasks = [handler.generate_insight(**sample_inputs) for _ in range(5)]
    results = await asyncio.gather(*tasks)
    
    assert len(results) == 5
    # Should call the agent once and cache the result
    assert mock_agent.ainvoke.call_count == 1

@pytest.mark.asyncio
async def test_cache_key_uniqueness(mock_llm, sample_inputs):
    """Test that cache keys are unique for different inputs."""
    handler, _, mock_cache = mock_llm
    
    # First call
    await handler.generate_insight(score=80, tags=["test"], explanations=[])
    
    # Different score
    await handler.generate_insight(score=90, tags=["test"], explanations=[])
    
    # Should have different cache keys
    assert len(mock_cache.set.await_args_list) == 2
    key1 = mock_cache.set.await_args_list[0][0][0]
    key2 = mock_cache.set.await_args_list[1][0][0]
    assert key1 != key2