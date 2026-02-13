from pydantic import BaseModel, Field


class Episode(BaseModel):
    id: str
    series_id: str | None = None
    title: str
    status: str = "ready"


class EpisodeCreate(BaseModel):
    title: str = Field(..., min_length=1)
    series_id: str | None = None


class EpisodeUpdate(BaseModel):
    title: str | None = None
    status: str | None = None
