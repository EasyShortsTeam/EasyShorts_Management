from datetime import datetime
from pydantic import BaseModel


class Message(BaseModel):
    message: str


class HealthResponse(BaseModel):
    status: str = "ok"
    time: datetime
    app: str
    env: str
