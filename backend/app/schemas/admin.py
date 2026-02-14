from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class Page(BaseModel):
    items: list[Any]
    total: int
    limit: int
    offset: int


class AdminUser(BaseModel):
    user_id: str
    email: str
    username: str
    is_active: int
    created_at: datetime | None = None

    plan: str | None = None
    credit: int | None = None
    oauth_provider: str | None = None


class AdminEpisode(BaseModel):
    episode_id: str
    user_id: str | None = None
    title: str | None = None
    series_layout: str | None = None
    error: str | None = None
    created_at: datetime | None = None

    video_url: str | None = None
    preview_video_url: str | None = None


class AdminJob(BaseModel):
    job_id: str
    job_type: str
    status: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
    result: Any | None = None
    error: str | None = None


class CreditPatch(BaseModel):
    mode: str = Field(default='set', description="set|add")
    amount: int = Field(..., description="set: absolute credit, add: delta (+/-)")
    reason: str | None = None


class PlanPatch(BaseModel):
    plan: str


class ActivePatch(BaseModel):
    is_active: int = Field(..., description="1 active, 0 inactive")


class AssetItem(BaseModel):
    key: str
    size: int | None = None
    last_modified: datetime | None = None
    url: str | None = None
