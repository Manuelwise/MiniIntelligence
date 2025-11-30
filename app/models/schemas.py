from pydantic import BaseModel, Field
from typing import List, Optional
from pydantic import ConfigDict  # for v2 config

class LLMOutput(BaseModel):
    insight: str
    recommendations: List[str] = Field(default_factory=list)
    key_points: List[str] = Field(default_factory=list)

    # Pydantic v2 config
    model_config = ConfigDict(extra="forbid")

class Insight(BaseModel):
    key_points: List[str]
    summary: str
    recommended_action: str
    model_config = ConfigDict(extra="forbid")

class Task(BaseModel):
    id: str
    title: str
    planned_minutes: int
    actual_minutes: Optional[int] = None
    completed: bool = False
    category: Optional[str] = None
    model_config = ConfigDict(extra="forbid")

class InputPayload(BaseModel):
    user_id: Optional[str] = None
    date_range: Optional[str] = None
    tasks: List[Task]
    deep_work_minutes: int
    meetings_minutes: int
    interruptions: int
    sleep_hours: float
    breaks_minutes: int
    mood: Optional[int] = None
    notes: Optional[str] = None
    model_config = ConfigDict(extra="forbid")

class RuleExplanation(BaseModel):
    rule_id: str
    description: str
    effect_on_score: float
    model_config = ConfigDict(extra="forbid")

class AnalyseResult(BaseModel):
    score: float
    tags: List[str]
    explanations: List[RuleExplanation]
    llm: Optional[LLMOutput] = None
