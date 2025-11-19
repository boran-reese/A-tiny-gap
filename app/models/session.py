from datetime import datetime, date
import enum
import uuid

from sqlalchemy import Column, Date, DateTime, Enum, ForeignKey, JSON, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class MoodEnum(str, enum.Enum):
    TIRED = "TIRED"
    ANXIOUS = "ANXIOUS"
    CALM = "CALM"
    NUMB = "NUMB"
    UNKNOWN = "UNKNOWN"
    CALMER = "CALMER"


class SessionStatus(str, enum.Enum):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    ABANDONED = "ABANDONED"


class PlaySession(Base):
    __tablename__ = "play_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    date = Column(Date, default=date.today, nullable=False)
    start_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    end_at = Column(DateTime, nullable=True)
    initial_mood = Column(Enum(MoodEnum), default=MoodEnum.UNKNOWN, nullable=False)
    final_mood = Column(Enum(MoodEnum), default=MoodEnum.UNKNOWN, nullable=False)
    director_plan = Column(JSON, nullable=True)
    status = Column(Enum(SessionStatus), default=SessionStatus.IN_PROGRESS, nullable=False)

    interactions = relationship("SessionInteraction", back_populates="session")


class SessionInteraction(Base):
    __tablename__ = "session_interactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("play_sessions.id"), nullable=False, index=True)
    type = Column(String(50), nullable=False)
    payload = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    session = relationship("PlaySession", back_populates="interactions")
