from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

import boto3
from botocore.client import Config

from app.core.config import settings


@dataclass
class ListedAsset:
    key: str
    size: int | None = None
    last_modified: datetime | None = None
    url: str | None = None


def _s3_client():
    # boto3 will read env creds automatically; we also support explicit settings.
    session = boto3.session.Session(
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        region_name=settings.aws_region,
    )
    return session.client('s3', config=Config(signature_version='s3v4'))


def list_s3_objects(bucket: str, prefix: str = '') -> list[ListedAsset]:
    client = _s3_client()
    paginator = client.get_paginator('list_objects_v2')

    items: list[ListedAsset] = []
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get('Contents', []) or []:
            key = obj.get('Key')
            if not key or key.endswith('/'):
                continue
            items.append(
                ListedAsset(
                    key=key,
                    size=int(obj.get('Size') or 0),
                    last_modified=obj.get('LastModified'),
                )
            )
    return items


def upload_s3(bucket: str, key: str, file_path: Path, content_type: str | None = None) -> None:
    client = _s3_client()
    extra = {}
    if content_type:
        extra['ContentType'] = content_type
    client.upload_file(str(file_path), bucket, key, ExtraArgs=extra or None)


def list_local_assets(base_dir: Path) -> list[ListedAsset]:
    if not base_dir.exists():
        return []
    items: list[ListedAsset] = []
    for p in base_dir.rglob('*'):
        if not p.is_file():
            continue
        stat = p.stat()
        items.append(
            ListedAsset(
                key=str(p.relative_to(base_dir)).replace('\\', '/'),
                size=stat.st_size,
                last_modified=datetime.fromtimestamp(stat.st_mtime),
            )
        )
    return items


def delete_s3_object(bucket: str, key: str) -> None:
    client = _s3_client()
    client.delete_object(Bucket=bucket, Key=key)


def parse_s3_url(url: str) -> tuple[str, str] | None:
    """Return (bucket, key) if url looks like an S3 object URL."""
    from urllib.parse import urlparse

    try:
        u = urlparse(url)
    except Exception:
        return None

    if u.scheme not in ("http", "https"):
        return None

    host = (u.netloc or "").split(":")[0]
    path = (u.path or "").lstrip("/")

    # virtual-hosted-style: {bucket}.s3.{region}.amazonaws.com/{key}
    if ".s3." in host and host.endswith("amazonaws.com"):
        bucket = host.split(".s3.")[0]
        key = path
        if bucket and key:
            return bucket, key

    # path-style: s3.{region}.amazonaws.com/{bucket}/{key}
    if host.startswith("s3.") and host.endswith("amazonaws.com") and "/" in path:
        bucket, key = path.split("/", 1)
        if bucket and key:
            return bucket, key

    return None
