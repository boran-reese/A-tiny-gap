from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models.growth import GrowthEvent, GrowthStats
from app.models.profile import UserProfile
from app.models.session import MoodEnum, PlaySession
from app.schemas.growth import GrowthEventRead, GrowthHistoryResponse, GrowthStatsRead
from app.schemas.history import MoodHistoryPoint, MoodHistoryResponse
from app.schemas.user import UserProfileBase, UserProfileRead

router = APIRouter()


def _ensure_growth_stats(db: Session, user_id):
    stats = db.query(GrowthStats).filter(GrowthStats.user_id == user_id).first()
    if stats is None:
        stats = GrowthStats(user_id=user_id)
        db.add(stats)
        db.commit()
        db.refresh(stats)
    return stats


@router.get("/profile", response_model=UserProfileRead)
def get_profile(db: Session = Depends(get_db), user=Depends(get_current_user)):
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    if profile is None:
        profile = UserProfile(user_id=user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return UserProfileRead.from_orm(profile)


@router.patch("/profile", response_model=UserProfileRead)
def update_profile(payload: UserProfileBase, db: Session = Depends(get_db), user=Depends(get_current_user)):
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    if profile is None:
        profile = UserProfile(user_id=user.id)
    if payload.nickname is not None:
        profile.nickname = payload.nickname
    if payload.preferred_play_time is not None:
        profile.preferred_play_time = payload.preferred_play_time
    if payload.play_style is not None:
        profile.play_style = payload.play_style
    if payload.onboarding_done is not None:
        profile.onboarding_done = payload.onboarding_done
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return UserProfileRead.from_orm(profile)


@router.get("/growth", response_model=GrowthHistoryResponse)
def growth_history(db: Session = Depends(get_db), user=Depends(get_current_user)):
    stats = _ensure_growth_stats(db, user.id)
    events = (
        db.query(GrowthEvent)
        .filter(GrowthEvent.user_id == user.id)
        .order_by(GrowthEvent.created_at.desc())
        .limit(20)
        .all()
    )
    return GrowthHistoryResponse(
        stats=GrowthStatsRead(
            emotional_awareness=stats.emotional_awareness,
            self_boundary=stats.self_boundary,
            cognitive_flexibility=stats.cognitive_flexibility,
            expression_ability=stats.expression_ability,
            updated_at=stats.updated_at,
        ),
        events=[
            GrowthEventRead(
                dimension=event.dimension,
                delta=event.delta,
                source=event.source,
                created_at=event.created_at,
            )
            for event in events
        ],
    )


@router.get("/history/mood", response_model=MoodHistoryResponse)
def mood_history(db: Session = Depends(get_db), user=Depends(get_current_user)):
    sessions = (
        db.query(PlaySession)
        .filter(PlaySession.user_id == user.id)
        .order_by(PlaySession.date.desc())
        .limit(30)
        .all()
    )
    points = []
    for session in sessions:
        mood = session.final_mood
        if mood == MoodEnum.UNKNOWN:
            mood = session.initial_mood
        points.append(MoodHistoryPoint(date=session.date, mood=mood))
    points.reverse()
    return MoodHistoryResponse(points=points)
