from datetime import datetime
import uuid

from enum import Enum

from sqlalchemy import Column, DateTime, Enum as SAEnum, ForeignKey, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class PreferredPlayTime(str, Enum):
    MORNING = "MORNING"
    EVENING = "EVENING"
    FLEXIBLE = "FLEXIBLE"


class PlayStyle(str, Enum):
    SHORT = "SHORT"
    EXPLORATION = "EXPLORATION"
    STORY = "STORY"


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    nickname = Column(String(50), nullable=True)
    preferred_play_time = Column(SAEnum(PreferredPlayTime), default=PreferredPlayTime.FLEXIBLE)
    play_style = Column(SAEnum(PlayStyle), default=PlayStyle.SHORT)
    onboarding_done = Column(Boolean, default=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="profile")
