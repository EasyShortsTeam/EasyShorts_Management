from pydantic import BaseModel, Field


class Series(BaseModel):
    id: str
    title: str
    description: str | None = None


class SeriesCreate(BaseModel):
    title: str = Field(..., min_length=1)
    description: str | None = None


class SeriesUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
