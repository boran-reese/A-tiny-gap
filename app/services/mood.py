from typing import List

from app.models.session import MoodEnum


def infer_initial_mood_from_entry_actions(actions: List[dict]) -> MoodEnum:
    if not actions:
        return MoodEnum.UNKNOWN

    power_sum = 0.0
    throws = 0
    for action in actions:
        if action.get("type") == "STONE_THROW":
            throws += 1
            payload = action.get("payload") or {}
            power_sum += float(payload.get("power", 0))

    if throws == 0:
        return MoodEnum.UNKNOWN

    avg_power = power_sum / throws
    if avg_power > 0.8:
        return MoodEnum.ANXIOUS
    if avg_power > 0.5:
        return MoodEnum.TIRED
    if avg_power > 0.2:
        return MoodEnum.CALM
    return MoodEnum.NUMB
