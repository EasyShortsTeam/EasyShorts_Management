from pydantic import BaseModel, Field


class Short(BaseModel):
    id: str
    title: str
    status: str = "draft"


class ShortCreate(BaseModel):
    title: str = Field(..., min_length=1)


class ShortUpdate(BaseModel):
    title: str | None = None
    status: str | None = None
