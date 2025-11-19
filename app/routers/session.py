from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models.session import PlaySession, SessionInteraction, SessionStatus
from app.schemas.session import (
    DirectorPlan,
    DirectorRecommendRequest,
    DirectorRecommendResponse,
    SessionCompleteRequest,
    SessionInteractionCreate,
    SessionStartRequest,
    SessionStartResponse,
)
from app.services.director import generate_plan_for_today, recommend_next_step
from app.services.mood import infer_initial_mood_from_entry_actions

router = APIRouter()


def _ensure_session_owner(db: Session, session_id: UUID, user_id: UUID) -> PlaySession:
    session = db.get(PlaySession, session_id)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    if session.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return session


@router.post("/start", response_model=SessionStartResponse)
def start_session(
    payload: SessionStartRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    today = payload.client_time.date()
    existing = (
        db.query(PlaySession)
        .filter(
            PlaySession.user_id == user.id,
            PlaySession.date == today,
            PlaySession.status == SessionStatus.IN_PROGRESS,
        )
        .first()
    )
    if existing:
        slots = existing.director_plan.get("episode_slots", []) if existing.director_plan else []
        return SessionStartResponse(
            session_id=existing.id,
            initial_mood=existing.initial_mood,
            plan=DirectorPlan(episode_slots=slots),
        )

    plan = generate_plan_for_today(db, user.id)
    mood = infer_initial_mood_from_entry_actions([action.dict() for action in payload.entry_actions or []])
    session = PlaySession(
        user_id=user.id,
        date=today,
        initial_mood=mood,
        director_plan={"episode_slots": plan},
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return SessionStartResponse(
        session_id=session.id,
        initial_mood=session.initial_mood,
        plan=DirectorPlan(episode_slots=plan),
    )


@router.post("/{session_id}/interaction", status_code=status.HTTP_201_CREATED)
def record_interaction(
    session_id: UUID,
    payload: SessionInteractionCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    session = _ensure_session_owner(db, session_id, user.id)
    interaction = SessionInteraction(session_id=session.id, type=payload.type, payload=payload.payload)
    db.add(interaction)
    db.commit()
    return {"status": "ok"}


@router.post("/{session_id}/director/recommend", response_model=DirectorRecommendResponse)
def director_recommend(
    session_id: UUID,
    payload: DirectorRecommendRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    session = _ensure_session_owner(db, session_id, user.id)
    recommendation = recommend_next_step(session.final_mood or session.initial_mood)
    return DirectorRecommendResponse(**recommendation)


@router.post("/{session_id}/complete")
def complete_session(
    session_id: UUID,
    payload: SessionCompleteRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    session = _ensure_session_owner(db, session_id, user.id)
    if session.status != SessionStatus.IN_PROGRESS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Session already closed")

    session.final_mood = payload.final_mood
    session.status = SessionStatus.COMPLETED
    session.end_at = datetime.utcnow()
    db.add(session)
    db.commit()
    return {"status": "completed", "session_id": str(session.id)}
