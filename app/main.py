from fastapi import FastAPI

from app.database import init_db
from app.routers import auth, profile, session, starlight, world

app = FastAPI(title="LittleGap Backend")


@app.on_event("startup")
def startup_event():
    init_db()


app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(session.router, prefix="/session", tags=["session"])
app.include_router(world.router, prefix="/world", tags=["world"])
app.include_router(starlight.router, prefix="/starlight", tags=["starlight"])
app.include_router(profile.router, prefix="/me", tags=["me"])
