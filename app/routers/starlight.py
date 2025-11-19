import random

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models.starlight import StarlightMessage
from app.schemas.starlight import StarlightDrawResponse, StarlightMessageRead, StarlightSendRequest

router = APIRouter()


@router.post("/send", response_model=StarlightMessageRead)
def send_message(payload: StarlightSendRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    message = StarlightMessage(
        from_user_id=user.id,
        content=payload.content,
        tags=payload.tags,
        language=payload.language,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return StarlightMessageRead.from_orm(message)


@router.post("/draw", response_model=StarlightDrawResponse)
def draw_message(db: Session = Depends(get_db), user=Depends(get_current_user)):
    candidates = (
        db.query(StarlightMessage)
        .filter(StarlightMessage.approved.is_(True), StarlightMessage.to_user_id.is_(None))
        .order_by(StarlightMessage.created_at.desc())
        .limit(10)
        .all()
    )
    if not candidates:
        return StarlightDrawResponse(status="empty", message=None)
    message = random.choice(candidates)
    message.to_user_id = user.id
    db.add(message)
    db.commit()
    db.refresh(message)
    return StarlightDrawResponse(status="ok", message=StarlightMessageRead.from_orm(message))
