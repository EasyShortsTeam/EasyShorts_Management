from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional
from uuid import uuid4

from app.schemas.credits import (
    CreditAdjustRequest,
    CreditLedgerEntry,
    CreditUserDetail,
    CreditUserSummary,
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class _UserCredits:
    user_id: str
    email: str
    username: str
    credits_balance: int
    updated_at: datetime
    ledger: List[CreditLedgerEntry]


# NOTE: In-memory store (scaffold). Replace with DB.
_STORE: Dict[str, _UserCredits] = {}


def _seed_if_empty() -> None:
    if _STORE:
        return
    t = _now()
    for i, (email, username, credits) in enumerate(
        [
            ("admin@example.com", "admin", 9999),
            ("user1@example.com", "user1", 120),
            ("user2@example.com", "user2", 0),
        ],
        start=1,
    ):
        user_id = str(i)
        _STORE[user_id] = _UserCredits(
            user_id=user_id,
            email=email,
            username=username,
            credits_balance=credits,
            updated_at=t,
            ledger=[],
        )


def list_users(query: Optional[str] = None) -> list[CreditUserSummary]:
    _seed_if_empty()
    items = list(_STORE.values())
    if query:
        q = query.lower().strip()
        items = [
            u
            for u in items
            if q in u.user_id.lower() or q in u.email.lower() or q in u.username.lower()
        ]
    return [
        CreditUserSummary(
            user_id=u.user_id,
            email=u.email,
            username=u.username,
            credits_balance=u.credits_balance,
            updated_at=u.updated_at,
        )
        for u in items
    ]


def get_user(user_id: str) -> CreditUserDetail:
    _seed_if_empty()
    if user_id not in _STORE:
        # auto-create placeholder user for convenience in admin
        t = _now()
        _STORE[user_id] = _UserCredits(
            user_id=user_id,
            email=f"user{user_id}@example.com",
            username=f"user{user_id}",
            credits_balance=0,
            updated_at=t,
            ledger=[],
        )
    u = _STORE[user_id]
    return CreditUserDetail(
        user_id=u.user_id,
        email=u.email,
        username=u.username,
        credits_balance=u.credits_balance,
        updated_at=u.updated_at,
        ledger=list(u.ledger)[-50:][::-1],
    )


def adjust_user(user_id: str, req: CreditAdjustRequest, actor: Optional[str] = None) -> CreditUserDetail:
    _seed_if_empty()
    u = _STORE.get(user_id)
    if not u:
        u = _UserCredits(
            user_id=user_id,
            email=f"user{user_id}@example.com",
            username=f"user{user_id}",
            credits_balance=0,
            updated_at=_now(),
            ledger=[],
        )
        _STORE[user_id] = u

    u.credits_balance += int(req.delta)
    u.updated_at = _now()

    entry = CreditLedgerEntry(
        id=str(uuid4()),
        user_id=user_id,
        delta=int(req.delta),
        reason=req.reason,
        created_at=u.updated_at,
        actor=actor,
    )
    u.ledger.append(entry)

    return get_user(user_id)
