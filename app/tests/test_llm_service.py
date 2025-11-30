import json
from typing import List
from langchain_openai import ChatOpenAI  # LangChain 1.0+
from langchain_core.prompts import PromptTemplate, MessagesPlaceholder
from langchain.agents.openai_functions_agent.agent_token_buffer_memory import AgentTokenBufferMemory
from langchain.agents.openai_functions_agent.base import OpenAIFunctionsAgent
from langchain_core.messages import SystemMessage
from app.utils.cache import cache
from app.config import get_settings
from app.models.schemas import LLMOutput, RuleExplanation

settings = get_settings()


class LLMHandler:
    """
    Handles LLM calls using the new LangChain 1.0+ Agent API,
    with structured JSON output via Pydantic models and caching.
    """

    def __init__(
        self,
        model_name: str = settings.LLM_MODEL,
        temperature: float = settings.LLM_TEMPERATURE,
    ):
        # Initialize ChatOpenAI
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            openai_api_key=settings.LLM_API_KEY
        )

        # Prompt template
        template = """
You are a productivity analysis expert.
Use the following inputs:
Score: {score}
Tags: {tags}
Explanations: {explanations}

Provide a detailed analysis with:
1. Insight: A brief summary of the productivity
2. Recommendations: Actionable advice (as a list)
3. Key Points: Important observations (as a list)

Return JSON matching the following format:
{{
    "insight": "...",
    "recommendations": ["...", "..."],
    "key_points": ["...", "..."]
}}
"""
        self.prompt = PromptTemplate(
            template=template,
            input_variables=["score", "tags", "explanations"]
        )

        # Create agent (simple LLM-only agent, no tools)
        self.agent = create_openai_functions_agent(
            llm=self.llm,
            system_message=SystemMessage(content="You are a productivity assistant."),
        )

    async def generate_insight(
        self,
        score: float,
        tags: List[str],
        explanations: List[RuleExplanation]
    ):
        explanations_dict = [e.model_dump() for e in explanations]

        # Cache key
        cache_key = f"llm:insight:{score}:{json.dumps(tags)}:{json.dumps(explanations_dict)}"

        # Check cache
        cached = await cache.get(cache_key)
        if cached:
            return LLMOutput(**cached), True

        # Prepare input string
        input_text = self.prompt.format(
            score=score,
            tags=", ".join(tags),
            explanations="\n".join([f"- {e}" for e in explanations_dict])
        )

        # Call the agent
        try:
            response_text: str = await self.agent.arun(input_text)

            # Parse JSON into LLMOutput
            result_dict = json.loads(response_text)
            result = LLMOutput(**result_dict)

        except Exception as e:
            # Fallback on error
            result = LLMOutput(
                insight="AI error occurred.",
                recommendations=[f"Error: {str(e)}"],
                key_points=[]
            )
            return result, False

        # Cache result
        await cache.set(cache_key, result.model_dump(), expire=settings.CACHE_EXPIRE_SECONDS)

        return result, False
