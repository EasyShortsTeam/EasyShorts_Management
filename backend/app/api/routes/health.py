from datetime import datetime, timezone

from fastapi import APIRouter

from app.core.config import settings
from app.schemas.common import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(
        status="ok",
        time=datetime.now(timezone.utc),
        app=settings.app_name,
        env=settings.app_env,
    )
