import logging
from typing import List, Dict, Any
import json
from tenacity import retry, stop_after_attempt, wait_exponential
from pydantic import validate_arguments, Field
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from app.config import get_settings
from app.utils.cache import redis_cache as cache
from app.models.schemas import LLMOutput, RuleExplanation

logger = logging.getLogger(__name__)
settings = get_settings()

class LLMHandler:
    @validate_arguments
    def __init__(
        self,
        model_name: str = Field(default="llama-3.3-70b-versatile"),
        temperature: float = Field(default=0.7, ge=0, le=1),
    ):
        """Initialize the LLM handler with Groq model."""
        try:
            self.llm = ChatGroq(
                model_name=model_name,
                temperature=temperature,
                groq_api_key=settings.LLM_API_KEY,
                request_timeout=30
            )

            self.system_prompt = (
                "You are a productivity analysis expert. "
                "Analyze the provided score, tags, and explanations to generate: "
                "1. Insight: concise summary\n"
                "2. Recommendations: 3-5 actionable recommendations\n"
                "3. Key Points: 3-5 important observations\n"
                "Format your response as JSON with keys: insight, recommendations, key_points"
            )

            logger.info(f"Initialized LLMHandler with model: {model_name}")

        except Exception as e:
            logger.error(f"Failed to initialize LLMHandler: {str(e)}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10), reraise=True)
    async def _call_llm(self, input_text: str) -> Dict[str, Any]:
        """Call the LLM directly without using a React agent."""
        try:
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=input_text)
            ]

            response = await self.llm.agenerate([messages])
            if not response or not response.generations or not response.generations[0]:
                raise ValueError("Invalid response from LLM")

            output_text = response.generations[0][0].text
            return self._validate_llm_response(output_text)

        except Exception as e:
            logger.error(f"LLM API call failed: {str(e)}")
            raise

    def _validate_llm_response(self, response_content: Any) -> Dict[str, Any]:
        try:
            if isinstance(response_content, str):
                cleaned = response_content.strip()
                if cleaned.startswith("```json"):
                    cleaned = cleaned[7:-3].strip()
                parsed = json.loads(cleaned)
            elif isinstance(response_content, dict):
                parsed = response_content
            else:
                raise ValueError("Unexpected LLM response format")

            required_keys = {"insight", "recommendations", "key_points"}
            if not all(k in parsed for k in required_keys):
                raise ValueError(f"Missing keys in response: {required_keys - parsed.keys()}")

            if not isinstance(parsed["recommendations"], list):
                parsed["recommendations"] = [parsed["recommendations"]]
            if not isinstance(parsed["key_points"], list):
                parsed["key_points"] = [parsed["key_points"]]

            return parsed

        except Exception as e:
            logger.error(f"Error validating LLM response: {str(e)}")
            raise ValueError("Invalid JSON response from LLM")

    @validate_arguments
    async def generate_insight(
        self,
        score: float = Field(..., ge=0, le=100),
        tags: List[str] = Field(..., min_items=1),
        explanations: List[RuleExplanation] = Field(..., min_items=1)
    ) -> tuple[LLMOutput, bool]:
        try:
            explanations_dict = [e.model_dump() for e in explanations]
            cache_key = f"llm:insight:{score}:{json.dumps(sorted(tags))}:{json.dumps(explanations_dict, sort_keys=True)}"

            cached = await cache.get(cache_key)
            if cached:
                logger.debug("Cache hit for productivity insights")
                return LLMOutput(**cached), True

            input_text = (
                f"Score: {score}/100\n"
                f"Tags: {', '.join(sorted(tags))}\n"
                "Explanations:\n" + "\n".join([f"- {e}" for e in explanations_dict])
            )

            parsed_response = await self._call_llm(input_text)
            result = LLMOutput(**parsed_response)

            await cache.set(cache_key, result.model_dump(), expire=settings.CACHE_EXPIRE_SECONDS)
            return result, False

        except Exception as e:
            logger.error(f"Error generating insight: {str(e)}")
            return LLMOutput(
                insight="Error generating analysis",
                recommendations=[f"Please try again later: {str(e)}"],
                key_points=[]
            ), False
