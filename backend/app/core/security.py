"""JWT auth (HS256) for the admin backend.

This project (EasyShorts_Management) assumes EasyShorts_backend issues JWTs.
We verify those JWTs here and gate admin APIs by `role == 'admin'`.

Current assumptions (as provided):
- Algorithm: HS256
- Roles: admin | user
- Admin user is manually set in DB on EasyShorts_backend.

Env:
- JWT_SECRET (shared with EasyShorts_backend)

NOTE:
- This file intentionally does NOT mint tokens. It only verifies.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.core.config import settings


@dataclass
class UserContext:
    id: str
    email: str
    role: str
    raw: Dict[str, Any] | None = None


_bearer = HTTPBearer(auto_error=False)


def _decode_hs256_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        if not isinstance(payload, dict):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token")
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token")


def _to_user_context(payload: Dict[str, Any]) -> UserContext:
    # common JWT claim names
    user_id = payload.get("sub") or payload.get("user_id") or payload.get("id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token: missing subject")

    email = payload.get("email") or payload.get("user_email") or ""
    role = payload.get("role") or payload.get("user_role") or "user"

    if role not in ("admin", "user"):
        # fail closed
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token: unknown role")

    return UserContext(id=str(user_id), email=str(email), role=str(role), raw=payload)


def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer)) -> UserContext:
    """Return current user context from Bearer JWT.

    Raises 401 if token is missing or invalid.
    """

    if not credentials or credentials.scheme.lower() != "bearer" or not credentials.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="missing bearer token")

    payload = _decode_hs256_token(credentials.credentials)
    return _to_user_context(payload)


def require_admin(user: UserContext = Depends(get_current_user)) -> UserContext:
    """Gate for admin-only APIs."""

    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="admin only")
    return user
