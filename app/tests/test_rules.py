import pytest
from app.rules.rules_engine import compute_productivity 
from app.models.schemas import InputPayload, Task


def test_high_productivity():
    """High productivity: many completed tasks + strong deep work."""
    payload = InputPayload(
        user_id="1",
        date_range="2025-11-29",
        tasks=[
            Task(id="1", title="A", planned_minutes=60, actual_minutes=60, completed=True),
            Task(id="2", title="B", planned_minutes=45, actual_minutes=40, completed=True),
        ],
        deep_work_minutes=180,
        meetings_minutes=30,
        interruptions=1,
        sleep_hours=8,
        breaks_minutes=20,
        mood=9
    )

    result = analyse(payload)

    assert result.score >= 80
    assert "high_productivity" in result.tags
    assert "deep_work_mastery" in result.tags


def test_medium_productivity():
    """Balanced performance but not exceptional."""
    payload = InputPayload(
        user_id="1",
        date_range="2025-11-29",
        tasks=[
            Task(id="1", title="A", planned_minutes=60, actual_minutes=40, completed=True),
        ],
        deep_work_minutes=90,
        meetings_minutes=60,
        interruptions=3,
        sleep_hours=7,
        breaks_minutes=25,
        mood=7
    )

    result = analyse(payload)

    assert 60 <= result.score < 80
    assert "balanced_day" in result.tags


def test_low_productivity():
    """Low output, many interruptions, low mood."""
    payload = InputPayload(
        user_id="1",
        date_range="2025-11-29",
        tasks=[
            Task(id="1", title="A", planned_minutes=60, actual_minutes=10, completed=False),
        ],
        deep_work_minutes=15,
        meetings_minutes=120,
        interruptions=8,
        sleep_hours=4,
        breaks_minutes=10,
        mood=3
    )

    result = analyse(payload)

    assert result.score < 60
    assert "low_energy" in result.tags or "distraction_prone" in result.tags


def test_zero_deep_work():
    """Edge case: zero deep work should lower score."""
    payload = InputPayload(
        user_id="1",
        date_range="2025-11-29",
        tasks=[
            Task(id="1", title="A", planned_minutes=60, actual_minutes=30, completed=False),
        ],
        deep_work_minutes=0,
        meetings_minutes=60,
        interruptions=2,
        sleep_hours=7,
        breaks_minutes=20,
        mood=7
    )

    result = analyse(payload)

    assert result.score < 70
    assert "low_focus" in result.tags
