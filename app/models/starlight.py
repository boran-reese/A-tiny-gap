from datetime import datetime
import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, JSON, String
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class StarlightMessage(Base):
    __tablename__ = "starlight_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    from_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    to_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    content = Column(String(500), nullable=False)
    tags = Column(JSON, default=list)
    language = Column(String(10), default="zh")
    approved = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    picked_at = Column(DateTime, nullable=True)
