from fastapi import APIRouter
from backend.api import health, video, ui
api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(video.router, prefix="/api", tags=["video"])
api_router.include_router(ui.router, tags=["ui"])
