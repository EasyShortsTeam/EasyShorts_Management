from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class CreditUserSummary(BaseModel):
    user_id: str
    email: str
    username: str
    credits_balance: int = 0
    updated_at: datetime


class CreditAdjustRequest(BaseModel):
    delta: int = Field(..., description="Positive to add credits, negative to subtract")
    reason: str = Field(..., min_length=1, max_length=200)


class CreditLedgerEntry(BaseModel):
    id: str
    user_id: str
    delta: int
    reason: str
    created_at: datetime
    actor: Optional[str] = None


class CreditUserDetail(BaseModel):
    user_id: str
    email: str
    username: str
    credits_balance: int
    updated_at: datetime
    ledger: list[CreditLedgerEntry]


class CreditAdjustResponse(BaseModel):
    status: Literal["ok"] = "ok"
    user: CreditUserDetail
