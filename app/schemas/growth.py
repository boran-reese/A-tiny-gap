from datetime import datetime
from typing import List

from pydantic import BaseModel

from app.models.growth import GrowthDimension


class GrowthStatsRead(BaseModel):
    emotional_awareness: int
    self_boundary: int
    cognitive_flexibility: int
    expression_ability: int
    updated_at: datetime | None = None


class GrowthEventRead(BaseModel):
    dimension: GrowthDimension
    delta: int
    source: str | None = None
    created_at: datetime

    class Config:
        use_enum_values = True


class GrowthHistoryResponse(BaseModel):
    stats: GrowthStatsRead
    events: List[GrowthEventRead]
