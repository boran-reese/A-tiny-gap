from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.models.session import MoodEnum, PlaySession
from app.models.world import TownState


def build_director_prompt(user_id: str, recent_sessions: List[PlaySession], town_state: TownState | None) -> str:
    lines = [
        f"User {user_id} recent moods: "
        + ", ".join(session.final_mood.value for session in recent_sessions if session.final_mood)
    ]
    if town_state and town_state.state:
        lines.append(f"Town weather bias: {town_state.state.get('weather_bias', 'unknown')}")
    return "\n".join(lines)


def call_llm(prompt: str) -> Dict[str, Any]:
    # Placeholder - would call external LLM in production
    return {
        "today_plan": [
            {"slot": 1, "type": "RELAX"},
            {"slot": 2, "type": "EXPRESSION"},
        ],
        "tone": "GENTLE",
    }


def generate_plan_for_today(db: Session, user_id) -> List[Dict[str, Any]]:
    recent_sessions = (
        db.query(PlaySession)
        .filter(PlaySession.user_id == user_id)
        .order_by(PlaySession.start_at.desc())
        .limit(3)
        .all()
    )
    town_state = db.query(TownState).filter(TownState.user_id == user_id).first()

    prompt = build_director_prompt(str(user_id), recent_sessions, town_state)
    llm_result = call_llm(prompt)
    plan = llm_result.get("today_plan") or [{"slot": 1, "type": "RELAX"}]
    return plan


def recommend_next_step(current_mood: MoodEnum) -> Dict[str, Any]:
    if current_mood in (MoodEnum.ANXIOUS, MoodEnum.TIRED):
        return {
            "episode_id": 1,
            "episode_type": "RELAX",
            "reason": "user_recent_sessions_show_high_stress",
            "entry_node_key": "intro",
        }
    return {
        "episode_id": 2,
        "episode_type": "GROWTH",
        "reason": "user_is_ready_for_reflection",
        "entry_node_key": "start",
    }
