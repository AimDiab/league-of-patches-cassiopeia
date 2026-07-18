from fastapi import FastAPI

from app.api.classify import router as classify_router
from app.api.health import router as health_router

app = FastAPI(title="League of Patches - Cassiopeia")

app.include_router(health_router)
app.include_router(classify_router)
