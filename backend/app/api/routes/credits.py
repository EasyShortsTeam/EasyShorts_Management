from __future__ import annotations

from fastapi import APIRouter, Query

from app.schemas.credits import (
    CreditAdjustRequest,
    CreditAdjustResponse,
    CreditUserDetail,
    CreditUserSummary,
)
from app.services.credits import adjust_user, get_user, list_users

router = APIRouter()


@router.get('/admin/credits/users', response_model=list[CreditUserSummary])
def admin_list_credit_users(q: str | None = Query(default=None, description='Search by user_id/email/username')):
    return list_users(query=q)


@router.get('/admin/credits/users/{user_id}', response_model=CreditUserDetail)
def admin_get_credit_user(user_id: str):
    return get_user(user_id)


@router.post('/admin/credits/users/{user_id}/adjust', response_model=CreditAdjustResponse)
def admin_adjust_credit_user(user_id: str, req: CreditAdjustRequest):
    # NOTE: auth not implemented yet; actor is placeholder
    user = adjust_user(user_id=user_id, req=req, actor='admin')
    return CreditAdjustResponse(user=user)
