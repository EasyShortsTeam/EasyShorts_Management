from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from app.core.security import require_admin
from app.db.session import get_db
from app.db.tables import Credit, Episode, EpisodeMeta, EpisodeOutputs, Job, OAuth, Plan, User
from app.schemas.admin import (
    ActivePatch,
    AdminEpisode,
    AdminJob,
    AdminUser,
    AssetItem,
    CreditPatch,
    Page,
    PlanPatch,
)

from app.core.config import settings
from app.services.assets import list_local_assets, list_s3_objects, upload_s3

router = APIRouter(dependencies=[Depends(require_admin)])


def _page(items: list[Any], total: int, limit: int, offset: int) -> Page:
    return Page(items=items, total=total, limit=limit, offset=offset)


@router.get("/users", response_model=Page)
def admin_list_users(
    q: str | None = Query(default=None, description="search email/username"),
    is_active: int | None = Query(default=None, description="1|0"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    where = []
    if q:
        like = f"%{q}%"
        where.append(or_(User.email.like(like), User.username.like(like), User.user_id.like(like)))
    if is_active is not None:
        where.append(User.is_active == is_active)

    base = (
        select(
            User.user_id,
            User.email,
            User.username,
            User.is_active,
            User.created_at,
            Plan.plan,
            Credit.credit,
            OAuth.oauth_provider,
        )
        .select_from(User)
        .outerjoin(Plan, Plan.user_id == User.user_id)
        .outerjoin(Credit, Credit.user_id == User.user_id)
        .outerjoin(OAuth, OAuth.user_id == User.user_id)
    )

    if where:
        base = base.where(and_(*where))

    total = db.execute(select(func.count()).select_from(base.subquery())).scalar_one()
    rows = db.execute(base.order_by(User.created_at.desc()).limit(limit).offset(offset)).all()

    items = [
        AdminUser(
            user_id=r.user_id,
            email=r.email,
            username=r.username,
            is_active=r.is_active,
            created_at=r.created_at,
            plan=r.plan,
            credit=r.credit,
            oauth_provider=r.oauth_provider,
        )
        for r in rows
    ]

    return _page(items, total=total, limit=limit, offset=offset)


@router.patch("/users/{user_id}/credit", response_model=AdminUser)
def admin_patch_credit(
    user_id: str,
    payload: CreditPatch,
    db: Session = Depends(get_db),
):
    u: User | None = db.execute(select(User).where(User.user_id == user_id)).scalar_one_or_none()
    if not u:
        raise HTTPException(status_code=404, detail="user not found")

    c: Credit | None = db.execute(select(Credit).where(Credit.user_id == user_id)).scalar_one_or_none()
    if not c:
        c = Credit(user_id=user_id, credit=0)
        db.add(c)
        db.flush()

    if payload.mode == "set":
        c.credit = int(payload.amount)
    elif payload.mode == "add":
        c.credit = int(c.credit or 0) + int(payload.amount)
    else:
        raise HTTPException(status_code=400, detail="mode must be set|add")

    db.commit()

    # return refreshed projection
    row = db.execute(
        select(
            User.user_id,
            User.email,
            User.username,
            User.is_active,
            User.created_at,
            Plan.plan,
            Credit.credit,
            OAuth.oauth_provider,
        )
        .select_from(User)
        .outerjoin(Plan, Plan.user_id == User.user_id)
        .outerjoin(Credit, Credit.user_id == User.user_id)
        .outerjoin(OAuth, OAuth.user_id == User.user_id)
        .where(User.user_id == user_id)
    ).one()

    return AdminUser(
        user_id=row.user_id,
        email=row.email,
        username=row.username,
        is_active=row.is_active,
        created_at=row.created_at,
        plan=row.plan,
        credit=row.credit,
        oauth_provider=row.oauth_provider,
    )


@router.patch("/users/{user_id}/plan", response_model=AdminUser)
def admin_patch_plan(
    user_id: str,
    payload: PlanPatch,
    db: Session = Depends(get_db),
):
    u: User | None = db.execute(select(User).where(User.user_id == user_id)).scalar_one_or_none()
    if not u:
        raise HTTPException(status_code=404, detail="user not found")

    p: Plan | None = db.execute(select(Plan).where(Plan.user_id == user_id)).scalar_one_or_none()
    if not p:
        p = Plan(user_id=user_id, plan=payload.plan)
        db.add(p)
    else:
        p.plan = payload.plan
    db.commit()

    # reuse list projection
    row = db.execute(
        select(
            User.user_id,
            User.email,
            User.username,
            User.is_active,
            User.created_at,
            Plan.plan,
            Credit.credit,
            OAuth.oauth_provider,
        )
        .select_from(User)
        .outerjoin(Plan, Plan.user_id == User.user_id)
        .outerjoin(Credit, Credit.user_id == User.user_id)
        .outerjoin(OAuth, OAuth.user_id == User.user_id)
        .where(User.user_id == user_id)
    ).one()

    return AdminUser(
        user_id=row.user_id,
        email=row.email,
        username=row.username,
        is_active=row.is_active,
        created_at=row.created_at,
        plan=row.plan,
        credit=row.credit,
        oauth_provider=row.oauth_provider,
    )


@router.patch("/users/{user_id}/active", response_model=AdminUser)
def admin_patch_active(
    user_id: str,
    payload: ActivePatch,
    db: Session = Depends(get_db),
):
    u: User | None = db.execute(select(User).where(User.user_id == user_id)).scalar_one_or_none()
    if not u:
        raise HTTPException(status_code=404, detail="user not found")

    u.is_active = int(payload.is_active)
    db.commit()

    row = db.execute(
        select(
            User.user_id,
            User.email,
            User.username,
            User.is_active,
            User.created_at,
            Plan.plan,
            Credit.credit,
            OAuth.oauth_provider,
        )
        .select_from(User)
        .outerjoin(Plan, Plan.user_id == User.user_id)
        .outerjoin(Credit, Credit.user_id == User.user_id)
        .outerjoin(OAuth, OAuth.user_id == User.user_id)
        .where(User.user_id == user_id)
    ).one()

    return AdminUser(
        user_id=row.user_id,
        email=row.email,
        username=row.username,
        is_active=row.is_active,
        created_at=row.created_at,
        plan=row.plan,
        credit=row.credit,
        oauth_provider=row.oauth_provider,
    )


@router.get("/episodes", response_model=Page)
def admin_list_episodes(
    q: str | None = Query(default=None, description="search title/episode_id/user_id"),
    user_id: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    where = []
    if q:
        like = f"%{q}%"
        where.append(or_(Episode.episode_id.like(like), Episode.title.like(like), Episode.user_id.like(like)))
    if user_id:
        where.append(Episode.user_id == user_id)

    base = (
        select(
            Episode.episode_id,
            Episode.user_id,
            Episode.title,
            Episode.error,
            Episode.created_at,
            EpisodeMeta.series_layout,
            EpisodeOutputs.video_url,
            EpisodeOutputs.preview_video_url,
        )
        .select_from(Episode)
        .outerjoin(EpisodeMeta, EpisodeMeta.episode_id == Episode.episode_id)
        .outerjoin(EpisodeOutputs, EpisodeOutputs.episode_id == Episode.episode_id)
    )
    if where:
        base = base.where(and_(*where))

    total = db.execute(select(func.count()).select_from(base.subquery())).scalar_one()
    rows = db.execute(base.order_by(Episode.created_at.desc()).limit(limit).offset(offset)).all()

    items = [
        AdminEpisode(
            episode_id=r.episode_id,
            user_id=r.user_id,
            title=r.title,
            series_layout=r.series_layout,
            error=r.error,
            created_at=r.created_at,
            video_url=r.video_url,
            preview_video_url=r.preview_video_url,
        )
        for r in rows
    ]
    return _page(items, total=total, limit=limit, offset=offset)


@router.get("/jobs", response_model=Page)
def admin_list_jobs(
    status: str | None = Query(default=None, description="comma-separated statuses"),
    job_type: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    where = []
    if status:
        statuses = [s.strip() for s in status.split(",") if s.strip()]
        if statuses:
            where.append(Job.status.in_(statuses))
    if job_type:
        where.append(Job.job_type == job_type)

    base = select(Job)
    if where:
        base = base.where(and_(*where))

    total = db.execute(select(func.count()).select_from(base.subquery())).scalar_one()
    rows = db.execute(base.order_by(Job.created_at.desc()).limit(limit).offset(offset)).scalars().all()

    items = [
        AdminJob(
            job_id=j.job_id,
            job_type=j.job_type,
            status=j.status,
            created_at=j.created_at,
            updated_at=j.updated_at,
            result=j.result,
            error=j.error,
        )
        for j in rows
    ]

    return _page(items, total=total, limit=limit, offset=offset)


@router.get("/jobs/{job_id}", response_model=AdminJob)
def admin_get_job(job_id: str, db: Session = Depends(get_db)):
    j: Job | None = db.execute(select(Job).where(Job.job_id == job_id)).scalar_one_or_none()
    if not j:
        raise HTTPException(status_code=404, detail="job not found")
    return AdminJob(
        job_id=j.job_id,
        job_type=j.job_type,
        status=j.status,
        created_at=j.created_at,
        updated_at=j.updated_at,
        result=j.result,
        error=j.error,
    )


# --- Assets (S3 or local static) ---

def _resolve_bucket(kind: str) -> str | None:
    if kind == "fonts":
        return settings.s3_fonts_bucket
    if kind == "soundeffects":
        return settings.s3_soundeffects_bucket
    if kind == "userassets":
        return settings.s3_userassets_bucket
    return None


def _resolve_local_dir(kind: str):
    # /static/assets/{kind}/*
    from pathlib import Path

    return Path("app/static") / "assets" / kind


@router.get("/assets/{kind}", response_model=list[AssetItem])
def admin_list_assets(kind: str, prefix: str = Query(default="")):
    bucket = _resolve_bucket(kind)
    if bucket:
        items = list_s3_objects(bucket=bucket, prefix=prefix or "")
        return [AssetItem(key=i.key, size=i.size, last_modified=i.last_modified, url=i.url) for i in items]

    base = _resolve_local_dir(kind)
    items = list_local_assets(base)
    if prefix:
        items = [i for i in items if i.key.startswith(prefix)]

    # Local URL points to mounted /static
    return [AssetItem(key=i.key, size=i.size, last_modified=i.last_modified, url=f"/static/assets/{kind}/{i.key}") for i in items]


@router.post("/assets/{kind}/upload", response_model=AssetItem)
async def admin_upload_asset(kind: str, key: str = Query(...), file: UploadFile = File(...)):
    bucket = _resolve_bucket(kind)

    # sanitize key
    key = (key or "").replace("..", "").lstrip("/")
    if not key:
        raise HTTPException(status_code=400, detail="key required")

    if bucket:
        from pathlib import Path

        tmp_dir = Path(".tmp_uploads")
        tmp_dir.mkdir(parents=True, exist_ok=True)
        tmp_path = tmp_dir / (file.filename or "upload.bin")
        content = await file.read()
        tmp_path.write_bytes(content)

        upload_s3(bucket=bucket, key=key, file_path=tmp_path, content_type=file.content_type)
        return AssetItem(key=key)

    # local mode
    base = _resolve_local_dir(kind)
    dest = base / key
    dest.parent.mkdir(parents=True, exist_ok=True)
    content = await file.read()
    dest.write_bytes(content)

    return AssetItem(key=key, size=dest.stat().st_size, url=f"/static/assets/{kind}/{key}")
