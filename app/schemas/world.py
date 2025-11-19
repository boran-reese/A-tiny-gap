from datetime import datetime
from typing import Any, Dict
from uuid import UUID

from pydantic import BaseModel


class TownStateRead(BaseModel):
    id: UUID
    version: int
    state: Dict[str, Any]
    updated_at: datetime | None = None

    class Config:
        orm_mode = True


class TownStateUpdate(BaseModel):
    version: int | None = None
    state: Dict[str, Any]
