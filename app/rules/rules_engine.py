from typing import List, Tuple
from app.models.schemas import InputPayload, RuleExplanation
from app.config import get_settings

settings = get_settings()

TARGET_DEEP_WORK = settings.TARGET_DEEP_WORK
TARGET_SLEEP = settings.TARGET_SLEEP
MAX_INTERRUPTION = settings.MAX_INTERRUPTION
MAX_MEETINGS = settings.MAX_MEETINGS


def compute_productivity(payload: InputPayload) -> Tuple[float, List[str], List[RuleExplanation]]:
    explanations = []
    score = 50.0  # base

    # 1) Task completion
    total_tasks = len(payload.tasks)
    completed = sum(1 for t in payload.tasks if t.completed)
    completion_rate = (completed / total_tasks) if total_tasks > 0 else 1.0
    effect = (completion_rate - 0.7) * 20  # completion around 70% is baseline
    score += effect
    explanations.append(RuleExplanation(
        rule_id="task_completion",
        description=f"Completion rate {completed}/{total_tasks} = {completion_rate:.2f}",
        effect_on_score=effect
    ))

    # 2) Deep work minutes
    deep = payload.deep_work_minutes
    if deep >= TARGET_DEEP_WORK:
        effect = min(15, (deep - TARGET_DEEP_WORK) / 10)
    else:
        effect = - (TARGET_DEEP_WORK - deep) / 10
    score += effect
    explanations.append(RuleExplanation(
        rule_id="deep_work",
        description=f"Deep work {deep} minutes (target {TARGET_DEEP_WORK})",
        effect_on_score=effect
    ))

    # 3) Meetings penalty
    meetings = payload.meetings_minutes
    meeting_penalty = - max(0, (meetings - MAX_MEETINGS) / 30) * 5
    score += meeting_penalty
    explanations.append(RuleExplanation(
        rule_id="meetings",
        description=f"Meetings {meetings} minutes (max healthy {MAX_MEETINGS})",
        effect_on_score=meeting_penalty
    ))

    # 4) Interruptions penalty
    intr = payload.interruptions
    intr_penalty = - min(15, (intr / MAX_INTERRUPTION) * 10)
    score += intr_penalty
    explanations.append(RuleExplanation(
        rule_id="interruptions",
        description=f"Interruptions {intr}",
        effect_on_score=intr_penalty
    ))

    # 5) Sleep effect
    sleep = payload.sleep_hours
    if sleep < TARGET_SLEEP:
        sleep_penalty = - (TARGET_SLEEP - sleep) * 3
    else:
        sleep_penalty = min(6, (sleep - TARGET_SLEEP) * 1.5)
    score += sleep_penalty
    explanations.append(RuleExplanation(
        rule_id="sleep",
        description=f"Sleep {sleep} hours (target {TARGET_SLEEP})",
        effect_on_score=sleep_penalty
    ))

    # 6) Breaks (benign)
    breaks = payload.breaks_minutes
    break_effect = min(5, (breaks / 30))
    score += break_effect
    explanations.append(RuleExplanation(
        rule_id="breaks",
        description=f"Breaks {breaks} minutes",
        effect_on_score=break_effect
    ))

    # 7) Mood bonus
    if payload.mood:
        mood_effect = (payload.mood - 5) * 1.5
        score += mood_effect
        explanations.append(RuleExplanation(
            rule_id="mood",
            description=f"Mood rating {payload.mood} (1-10)",
            effect_on_score=mood_effect
        ))

    # Normalize to 0-100
    score = max(0.0, min(100.0, score))

    # Tags
    tags = []
    if intr > MAX_INTERRUPTION * 0.8:
        tags.append("Distracted")
    if sleep < TARGET_SLEEP - 1.5:
        tags.append("BurnoutRisk")
    if deep >= TARGET_DEEP_WORK and completion_rate >= 0.8 and intr < MAX_INTERRUPTION * 0.4:
        tags.append("Focused")
    if 40 <= score <= 70:
        tags.append("NeedsImprovement")
    if score > 80:
        tags.append("WellBalanced")

    return score, tags, explanations
