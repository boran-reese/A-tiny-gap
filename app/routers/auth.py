from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models.profile import UserProfile
from app.models.user import User
from app.schemas.user import (
    AuthResponse,
    RefreshRequest,
    TokenPayload,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserRead,
)
from app.deps import get_current_user
from app.utils.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)

router = APIRouter()
settings = get_settings()


def _build_auth_response(user: User) -> AuthResponse:
    access = create_access_token(str(user.id))
    refresh = create_refresh_token(str(user.id))
    return AuthResponse(
        user=UserRead.from_orm(user),
        tokens=TokenResponse(access_token=access, refresh_token=refresh),
    )


@router.post("/register", response_model=AuthResponse)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user = User(email=payload.email, password_hash=hash_password(payload.password))
    db.add(user)
    db.flush()

    profile = UserProfile(user_id=user.id, nickname=payload.nickname)
    db.add(profile)
    db.commit()
    db.refresh(user)
    db.refresh(profile)
    user.profile = profile

    return _build_auth_response(user)


@router.post("/login", response_model=AuthResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    user.last_login_at = datetime.utcnow()
    db.add(user)
    db.commit()
    db.refresh(user)

    return _build_auth_response(user)


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest):
    try:
        decoded = jwt.decode(
            payload.refresh_token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        token_data = TokenPayload(**decoded)
    except (JWTError, ValueError):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid refresh token")

    access = create_access_token(token_data.sub)
    refresh_token = create_refresh_token(token_data.sub)
    return TokenResponse(access_token=access, refresh_token=refresh_token)


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)):
    return UserRead.from_orm(current_user)
