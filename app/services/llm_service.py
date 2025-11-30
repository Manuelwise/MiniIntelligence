import json
from typing import List
from langchain_openai import ChatOpenAI 
from langchain.agents.agent import AgentExecutor
from langchain.agents.openai_functions_agent.agent_token_buffer_memory import AgentTokenBufferMemory
from langchain.agents.openai_functions_agent.base import OpenAIFunctionsAgent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, HumanMessage
from app.utils.cache import cache
from app.config import get_settings
from app.models.schemas import LLMOutput, RuleExplanation

settings = get_settings()


class LLMHandler:
    def __init__(
        self,
        model_name: str = settings.LLM_MODEL,
        temperature: float = settings.LLM_TEMPERATURE
    ):
        # Initialize Chat model
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            openai_api_key=settings.LLM_API_KEY
        )

        # System prompt for the agent
        self.system_prompt = SystemMessage(
            content=(
                "You are a productivity analysis expert. "
                "You receive Score, Tags, and Explanations and return a structured analysis "
                "with Insight (brief summary), Recommendations (list), and Key Points (list)."
            )
        )

        # Create agent executor 
        self.agent_executor: AgentExecutor = create_openai_functions_agent(
            llm=self.llm,
            system_message=self.system_prompt
        )

    async def generate_insight(
        self,
        score: float,
        tags: List[str],
        explanations: List[RuleExplanation]
    ):
        # Convert RuleExplanation objects → dicts
        explanations_dict = [e.model_dump() for e in explanations]

        # Cache key
        cache_key = f"llm:insight:{score}:{json.dumps(tags)}:{json.dumps(explanations_dict)}"

        # Check cache
        cached = await cache.get(cache_key)
        if cached:
            return LLMOutput(**cached), True

        # Construct human prompt
        human_prompt = HumanMessage(
            content=(
                f"Score: {score}\n"
                f"Tags: {', '.join(tags)}\n"
                f"Explanations:\n" + "\n".join([f"- {e}" for e in explanations_dict])
            )
        )

        try:
            # Run agent
            agent_response = await self.agent_executor.arun([self.system_prompt, human_prompt])

            if isinstance(agent_response, str):
                parsed = json.loads(agent_response)
            else:
                parsed = dict(agent_response)

            result = LLMOutput(**parsed)

        except Exception as e:
            result = LLMOutput(
                insight="AI error occurred.",
                recommendations=[f"Error: {str(e)}"],
                key_points=[]
            )

        # Cache result
        await cache.set(cache_key, result.model_dump(), expire=settings.CACHE_EXPIRE_SECONDS)

        return result, False
