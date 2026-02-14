from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.api.routes import (
    health_router,
    auth_router,
    series_router,
    episodes_router,
    shorts_router,
    media_router,
    admin_router,
    assets_router,
)


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Static: /static/*
    app.mount("/static", StaticFiles(directory="app/static"), name="static")

    # API: /api/*
    app.include_router(health_router, prefix="/api", tags=["health"])
    app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
    app.include_router(series_router, prefix="/api/series", tags=["series"])
    app.include_router(episodes_router, prefix="/api/episodes", tags=["episodes"])
    app.include_router(shorts_router, prefix="/api/shorts", tags=["shorts"])
    app.include_router(media_router, prefix="/api/media", tags=["media"])

    # Admin-only (requires role=admin)
    app.include_router(admin_router, prefix="/api/admin", tags=["admin"])
    app.include_router(assets_router, prefix="/api/admin", tags=["assets"])

    return app


app = create_app()
