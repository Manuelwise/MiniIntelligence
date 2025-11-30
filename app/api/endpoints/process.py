from fastapi import APIRouter, Request, Response
from app.services.rate_limit import limiter
from app.models.schemas import InputPayload, AnalyseResult, RuleExplanation
from app.rules.rules_engine import compute_productivity
from app.services.llm_service import LLMHandler
from app.config import get_settings

settings = get_settings()

router = APIRouter(prefix="/api/v1", tags=["Analysis"])

# Global LLM instance
llm = LLMHandler(
    model_name=settings.LLM_MODEL,
    temperature=settings.LLM_TEMPERATURE
)


@router.post("/analyze", response_model=AnalyseResult)
@limiter.limit(settings.RATE_LIMIT)
async def analyze(payload: InputPayload, request: Request, response: Response):
    """
    Main productivity analysis API.
    Steps:
      1. Execute rules engine
      2. Generate LLM insights (cached)
      3. Return combined structured response
    """

    # 1. Compute productivity rules
    score, tags, explanations = compute_productivity(payload)

    # Convert explanations into RuleExplanation objects for LLMHandler
    explanation_objs: list[RuleExplanation] = [
        RuleExplanation(
            rule_id=e.rule_id,
            description=e.description,
            effect_on_score=e.effect_on_score
        )
        for e in explanations
    ]

    # 2. Generate LLM insight (with caching)
    llm_out, from_cache = await llm.generate_insight(
        score=score,
        tags=tags,
        explanations=explanation_objs
    )

    # Add cache header for debugging / tests
    response.headers["x-cache"] = "HIT" if from_cache else "MISS"

    return AnalyseResult(
    score=score,
    tags=tags,
    explanations=explanations,
    llm=llm_out
)
