from datetime import date
from typing import List

from pydantic import BaseModel

from app.models.session import MoodEnum


class MoodHistoryPoint(BaseModel):
    date: date
    mood: MoodEnum


class MoodHistoryResponse(BaseModel):
    points: List[MoodHistoryPoint]
