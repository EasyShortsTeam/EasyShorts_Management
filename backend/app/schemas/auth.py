from pydantic import BaseModel


class User(BaseModel):
    id: str
    email: str
    role: str = "admin"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User
