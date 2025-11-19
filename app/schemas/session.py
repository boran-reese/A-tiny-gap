from datetime import datetime, date
from typing import Any, List, Optional
from uuid import UUID

from pydantic import BaseModel

from app.models.session import MoodEnum, SessionStatus


class EntryAction(BaseModel):
    type: str
    payload: dict[str, Any] | None = None


class SessionStartRequest(BaseModel):
    client_time: datetime
    entry_actions: List[EntryAction] | None = None


class DirectorPlan(BaseModel):
    episode_slots: List[dict[str, Any]]


class SessionStartResponse(BaseModel):
    session_id: UUID
    initial_mood: MoodEnum
    plan: DirectorPlan


class SessionInteractionCreate(BaseModel):
    type: str
    payload: dict[str, Any]


class DirectorRecommendRequest(BaseModel):
    context_node: Optional[str] = None
    prefer_light: Optional[bool] = None


class DirectorRecommendResponse(BaseModel):
    episode_id: int
    episode_type: str
    reason: str
    entry_node_key: str


class SessionCompleteRequest(BaseModel):
    final_mood: MoodEnum
    duration_seconds: int


class SessionRead(BaseModel):
    id: UUID
    user_id: UUID
    date: date
    status: SessionStatus
    initial_mood: MoodEnum
    final_mood: MoodEnum
    director_plan: dict[str, Any] | None

    class Config:
        orm_mode = True
