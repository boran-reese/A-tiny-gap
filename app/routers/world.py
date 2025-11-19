from copy import deepcopy

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models.world import TownState
from app.schemas.world import TownStateRead, TownStateUpdate

router = APIRouter()

DEFAULT_TOWN_STATE = {
    "weather_bias": "clear",
    "zones": {
        "riverside": {"light_level": 0.5, "unlocked": True},
        "garden": {"plants": 3, "growth_level": 1},
    },
    "symbols": {"boundaries": 1, "warm_lights": 2},
}


@router.get("/state", response_model=TownStateRead)
def get_state(db: Session = Depends(get_db), user=Depends(get_current_user)):
    state = db.query(TownState).filter(TownState.user_id == user.id).first()
    if state is None:
        state = TownState(user_id=user.id, state=deepcopy(DEFAULT_TOWN_STATE))
        db.add(state)
        db.commit()
        db.refresh(state)
    return TownStateRead.from_orm(state)


@router.patch("/state", response_model=TownStateRead)
def update_state(
    payload: TownStateUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    state = db.query(TownState).filter(TownState.user_id == user.id).first()
    if state is None:
        raise HTTPException(status_code=404, detail="State not found")

    if payload.version is not None:
        state.version = payload.version
    state.state = payload.state
    db.add(state)
    db.commit()
    db.refresh(state)
    return TownStateRead.from_orm(state)
