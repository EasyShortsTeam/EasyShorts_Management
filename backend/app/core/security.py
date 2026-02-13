"""Security utilities (placeholder).

Later:
- JWT encode/decode
- OAuth token exchange
- Role/permission checks
"""

from dataclasses import dataclass


@dataclass
class UserContext:
    id: str
    email: str
    role: str = "admin"


def get_current_user_stub() -> UserContext:
    # TODO: Replace with real auth
    return UserContext(id="u_admin_001", email="admin@easyshorts.local", role="admin")
