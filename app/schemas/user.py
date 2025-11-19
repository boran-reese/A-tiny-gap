from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.models.profile import PlayStyle, PreferredPlayTime


class UserProfileBase(BaseModel):
    nickname: Optional[str] = None
    preferred_play_time: PreferredPlayTime | None = None
    play_style: PlayStyle | None = None
    onboarding_done: Optional[bool] = None

    class Config:
        use_enum_values = True


class UserProfileRead(UserProfileBase):
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    created_at: datetime
    profile: Optional[UserProfileRead] = None

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    nickname: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    exp: int


class AuthResponse(BaseModel):
    user: UserRead
    tokens: TokenResponse


class RefreshRequest(BaseModel):
    refresh_token: str
