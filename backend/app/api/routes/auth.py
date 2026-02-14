from fastapi import APIRouter, Depends

from app.core.security import UserContext, get_current_user_verified
from app.schemas.auth import TokenResponse, User
from app.schemas.common import Message

router = APIRouter()


@router.get("/me", response_model=User)
def me(u: UserContext = Depends(get_current_user_verified)):
    return User(id=u.id, email=u.email, role=u.role)


@router.get("/login", response_model=Message)
def login_placeholder():
    return Message(message="placeholder: use social login (kakao/google) and then store access_token")


@router.get("/kakao", response_model=Message)
def kakao_login_placeholder():
    return Message(message="placeholder: redirect user to Kakao OAuth authorize URL")


@router.get("/kakao/callback", response_model=TokenResponse)
def kakao_callback_placeholder(code: str | None = None, state: str | None = None):
    # In real implementation, exchange 'code' for access_token, then issue JWT.
    # Placeholder response. Real implementation should happen in EasyShorts_backend.
    # This admin backend only verifies JWTs; it does not mint them.
    return TokenResponse(
        access_token="mock_access_token",
        token_type="bearer",
        user=User(id="unknown", email="", role="user"),
    )


@router.get("/google", response_model=Message)
def google_login_placeholder():
    return Message(message="placeholder: Google OAuth not implemented")
