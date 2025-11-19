from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel, Field


class StarlightSendRequest(BaseModel):
    content: str
    tags: List[str] = Field(default_factory=list)
    language: str = "zh"


class StarlightMessageRead(BaseModel):
    id: UUID
    content: str
    tags: List[str]
    language: str
    created_at: datetime

    class Config:
        orm_mode = True


class StarlightDrawResponse(BaseModel):
    status: str
    message: StarlightMessageRead | None = None
