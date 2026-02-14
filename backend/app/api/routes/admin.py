from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy import and_, func, or_, select, text
from sqlalchemy.orm import Session

from app.core.security import require_admin
from app.db.session import get_db
from app.db.tables import (
    Credit,
    CreditLog,
    Episode,
    EpisodeMeta,
    EpisodeOutputs,
    Job,
    OAuth,
    Order,
    Plan,
    StoryAsset,
    StoryShot,
    StoryTTSSegment,
    User,
)
from app.schemas.admin import (
    ActivePatch,
    AdminEpisode,
    AdminJob,
    AdminOverviewMetrics,
    AdminUser,
    AssetItem,
    CreditPatch,
    DailyAgg,
    EpisodeDeleteResult,
    Page,
    PlanPatch,
    StatusAgg,
)

from app.core.config import settings
from app.services.assets import delete_s3_object, list_local_assets, list_s3_objects, parse_s3_url, upload_s3

router = APIRouter(dependencies=[Depends(require_admin)])
# admin-only endpoints


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


@router.get("/metrics/overview", response_model=AdminOverviewMetrics)
def admin_metrics_overview(
    days: int = Query(default=14, ge=1, le=90),
    db: Session = Depends(get_db),
):
    # totals
    users_total = db.execute(select(func.count()).select_from(User)).scalar_one()
    users_active = db.execute(select(func.count()).select_from(User).where(User.is_active == 1)).scalar_one()
    episodes_total = db.execute(select(func.count()).select_from(Episode)).scalar_one()
    jobs_total = db.execute(select(func.count()).select_from(Job)).scalar_one()

    # grouped counts
    jobs_by_status_rows = db.execute(select(Job.status, func.count()).group_by(Job.status)).all()
    jobs_by_status = [StatusAgg(status=r[0], count=int(r[1]), amount_sum=None) for r in jobs_by_status_rows]

    orders_by_status_rows = db.execute(
        select(Order.status, func.count(), func.coalesce(func.sum(Order.amount), 0)).group_by(Order.status)
    ).all()
    orders_by_status = [StatusAgg(status=r[0], count=int(r[1]), amount_sum=int(r[2] or 0)) for r in orders_by_status_rows]

    # daily series (MySQL DATE())
    orders_daily_rows = db.execute(
        select(func.date(Order.created_at), func.count(), func.coalesce(func.sum(Order.amount), 0))
        .where(Order.created_at >= func.date_sub(func.now(), text(f"interval {int(days)} day")))
        .group_by(func.date(Order.created_at))
        .order_by(func.date(Order.created_at).asc())
    ).all()
    orders_daily = [DailyAgg(date=str(r[0]), count=int(r[1]), amount_sum=int(r[2] or 0)) for r in orders_daily_rows]

    credit_daily_rows = db.execute(
        select(func.date(CreditLog.created_at), func.count(), func.coalesce(func.sum(CreditLog.amount), 0))
        .where(CreditLog.created_at >= func.date_sub(func.now(), text(f"interval {int(days)} day")))
        .group_by(func.date(CreditLog.created_at))
        .order_by(func.date(CreditLog.created_at).asc())
    ).all()
    credit_logs_daily = [DailyAgg(date=str(r[0]), count=int(r[1]), amount_sum=int(r[2] or 0)) for r in credit_daily_rows]

    return AdminOverviewMetrics(
        users_total=int(users_total),
        users_active=int(users_active),
        episodes_total=int(episodes_total),
        jobs_total=int(jobs_total),
        jobs_by_status=jobs_by_status,
        orders_by_status=orders_by_status,
        orders_daily=orders_daily,
        credit_logs_daily=credit_logs_daily,
    )


@router.delete("/episodes/{episode_id}", response_model=EpisodeDeleteResult)
def admin_delete_episode(
    episode_id: str,
    delete_objects: bool = Query(default=True, description="delete s3/local objects if URLs exist"),
    db: Session = Depends(get_db),
):
    # Load episode and outputs first
    ep: Episode | None = db.execute(select(Episode).where(Episode.episode_id == episode_id)).scalar_one_or_none()
    if not ep:
        raise HTTPException(status_code=404, detail="episode not found")

    out: EpisodeOutputs | None = db.execute(
        select(EpisodeOutputs).where(EpisodeOutputs.episode_id == episode_id)
    ).scalar_one_or_none()

    urls: list[str] = []
    if out and out.video_url:
        urls.append(str(out.video_url))
    if out and out.preview_video_url:
        urls.append(str(out.preview_video_url))

    # Story assets may store only s3_key (no full url)
    story_keys = [
        str(r[0])
        for r in db.execute(select(StoryAsset.s3_key).where(StoryAsset.episode_id == episode_id)).all()
        if r and r[0]
    ]

    deleted_objects: list[str] = []
    failed_objects: list[str] = []

    if delete_objects:
        from pathlib import Path

        static_root = Path("app/static")

        # 1) delete by output URLs
        for url in urls:
            # local static
            if url.startswith("/static/"):
                rel = url[len("/static/") :].lstrip("/")
                p = static_root / rel
                try:
                    if p.exists() and p.is_file():
                        p.unlink()
                        deleted_objects.append(url)
                except Exception:
                    failed_objects.append(url)
                continue

            # s3 url
            parsed = parse_s3_url(url)
            if parsed:
                bucket, key = parsed
                try:
                    delete_s3_object(bucket=bucket, key=key)
                    deleted_objects.append(url)
                except Exception:
                    failed_objects.append(url)

        # 2) delete story assets by s3_key (bucket inferred)
        inferred_bucket: str | None = None
        for url in urls:
            parsed = parse_s3_url(url)
            if parsed:
                inferred_bucket = parsed[0]
                break
        # bucket selection heuristics
        bucket_for_results = settings.s3_results_bucket or inferred_bucket
        bucket_for_userassets = settings.s3_userassets_bucket

        if story_keys:
            seen: set[tuple[str, str]] = set()
            for key in story_keys:
                k = (key or "").lstrip("/")
                if not k:
                    continue

                # If s3_key is under userassets/* prefer userassets bucket
                bucket = None
                if k.startswith("userassets/") and bucket_for_userassets:
                    bucket = bucket_for_userassets
                else:
                    bucket = bucket_for_results

                if not bucket:
                    failed_objects.append(f"s3://(unknown-bucket)/{k}")
                    continue

                sig = (bucket, k)
                if sig in seen:
                    continue
                seen.add(sig)

                try:
                    delete_s3_object(bucket=bucket, key=k)
                    deleted_objects.append(f"s3://{bucket}/{k}")
                except Exception:
                    failed_objects.append(f"s3://{bucket}/{k}")

    # Delete DB rows (manual cascade to be safe)
    # story assets/tts/shots
    shot_ids = [
        int(r[0])
        for r in db.execute(select(StoryShot.id).where(StoryShot.episode_id == episode_id)).all()
    ]
    if shot_ids:
        db.query(StoryTTSSegment).filter(StoryTTSSegment.shot_id.in_(shot_ids)).delete(synchronize_session=False)

    db.query(StoryAsset).filter(StoryAsset.episode_id == episode_id).delete(synchronize_session=False)
    db.query(StoryShot).filter(StoryShot.episode_id == episode_id).delete(synchronize_session=False)

    db.query(EpisodeOutputs).filter(EpisodeOutputs.episode_id == episode_id).delete(synchronize_session=False)
    db.query(EpisodeMeta).filter(EpisodeMeta.episode_id == episode_id).delete(synchronize_session=False)
    db.query(Episode).filter(Episode.episode_id == episode_id).delete(synchronize_session=False)

    db.commit()

    return EpisodeDeleteResult(
        episode_id=episode_id,
        deleted_db=True,
        deleted_objects=deleted_objects,
        failed_objects=failed_objects,
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
