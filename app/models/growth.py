from datetime import datetime
import enum
import uuid

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class GrowthDimension(str, enum.Enum):
    EMOTIONAL_AWARENESS = "emotional_awareness"
    SELF_BOUNDARY = "self_boundary"
    COGNITIVE_FLEXIBILITY = "cognitive_flexibility"
    EXPRESSION_ABILITY = "expression_ability"


class GrowthStats(Base):
    __tablename__ = "growth_stats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    emotional_awareness = Column(Integer, default=0)
    self_boundary = Column(Integer, default=0)
    cognitive_flexibility = Column(Integer, default=0)
    expression_ability = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class GrowthEvent(Base):
    __tablename__ = "growth_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    session_id = Column(UUID(as_uuid=True), ForeignKey("play_sessions.id"), nullable=True)
    dimension = Column(Enum(GrowthDimension), nullable=False)
    delta = Column(Integer, default=0)
    source = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
