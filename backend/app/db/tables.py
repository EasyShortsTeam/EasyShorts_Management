"""Minimal SQLAlchemy table mappings for EasyShorts_backend database.

We keep this intentionally small: only columns needed by admin endpoints.
"""

from __future__ import annotations

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.sql import func

from app.db.models import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), nullable=False)
    is_active = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Plan(Base):
    __tablename__ = 'plan'

    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), ForeignKey('users.user_id', ondelete='CASCADE'), unique=True, index=True, nullable=False)
    plan = Column(String(50), default='free', nullable=False)
    plan_paid_at = Column(DateTime(timezone=True), nullable=True)


class Credit(Base):
    __tablename__ = 'credit'

    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), ForeignKey('users.user_id', ondelete='CASCADE'), unique=True, index=True, nullable=False)
    credit = Column(Integer, default=0, nullable=False)


class OAuth(Base):
    __tablename__ = 'oauth'

    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), ForeignKey('users.user_id', ondelete='CASCADE'), unique=True, index=True, nullable=False)
    oauth_provider = Column(String(20), nullable=True, index=True)


class Episode(Base):
    __tablename__ = 'episodes'

    id = Column(Integer, primary_key=True)
    episode_id = Column(String(255), unique=True, index=True, nullable=False)
    user_id = Column(String(255), ForeignKey('users.user_id', ondelete='CASCADE'), index=True, nullable=True)
    title = Column(String(500), nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class EpisodeMeta(Base):
    __tablename__ = 'episode_meta'

    id = Column(Integer, primary_key=True)
    episode_id = Column(String(255), ForeignKey('episodes.episode_id', ondelete='CASCADE'), unique=True, index=True, nullable=False)
    target_aspect = Column(String(50), default='9:16', nullable=False)
    series_layout = Column(String(50), nullable=True)
    target_duration_sec = Column(Float, nullable=True)


class EpisodeOutputs(Base):
    __tablename__ = 'episode_outputs'

    id = Column(Integer, primary_key=True)
    episode_id = Column(String(255), ForeignKey('episodes.episode_id', ondelete='CASCADE'), unique=True, index=True, nullable=False)
    video_url = Column(Text, nullable=True)
    preview_video_url = Column(Text, nullable=True)
    video_generated_at = Column(DateTime(timezone=True), nullable=True)


class Job(Base):
    __tablename__ = 'jobs'

    id = Column(Integer, primary_key=True)
    job_id = Column(String(255), unique=True, index=True, nullable=False)
    job_type = Column(String(100), nullable=False)
    status = Column(String(50), default='pending', nullable=False)
    result = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
