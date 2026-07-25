from __future__ import annotations

import enum
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ExtractionType(str, enum.Enum):
    TEXT = "text"
    PRICE = "price"
    NUMBER = "number"
    STATUS = "status"
    HTML = "html"
    ATTRIBUTE = "attribute"


class ConditionType(str, enum.Enum):
    ANY_CHANGE = "any_change"
    PRICE_DROP = "price_drop"
    PRICE_BELOW = "price_below"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    STATUS_NOT_OK = "status_not_ok"


class RunStatus(str, enum.Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CHANGED = "changed"
    NO_CHANGE = "no_change"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(512))
    display_name: Mapped[str] = mapped_column(String(120), default="Usuário")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    monitors: Mapped[list[Monitor]] = relationship(back_populates="owner", cascade="all, delete-orphan")


class Monitor(Base):
    __tablename__ = "monitors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(180))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    url: Mapped[str] = mapped_column(Text)
    selector: Mapped[str | None] = mapped_column(String(500), nullable=True)
    extraction_type: Mapped[ExtractionType] = mapped_column(Enum(ExtractionType), default=ExtractionType.TEXT)
    attribute_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    render_js: Mapped[bool] = mapped_column(Boolean, default=False)
    interval_minutes: Mapped[int] = mapped_column(Integer, default=30)
    condition_type: Mapped[ConditionType] = mapped_column(Enum(ConditionType), default=ConditionType.ANY_CHANGE)
    threshold: Mapped[float | None] = mapped_column(Float, nullable=True)
    keyword: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    last_checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    next_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    owner: Mapped[User] = relationship(back_populates="monitors")
    runs: Mapped[list[Run]] = relationship(back_populates="monitor", cascade="all, delete-orphan")
    snapshots: Mapped[list[Snapshot]] = relationship(back_populates="monitor", cascade="all, delete-orphan")
    notifications: Mapped[list[Notification]] = relationship(back_populates="monitor", cascade="all, delete-orphan")


class Run(Base):
    __tablename__ = "runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    monitor_id: Mapped[int] = mapped_column(ForeignKey("monitors.id", ondelete="CASCADE"), index=True)
    status: Mapped[RunStatus] = mapped_column(Enum(RunStatus), default=RunStatus.QUEUED)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    http_status: Mapped[int | None] = mapped_column(Integer, nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    value: Mapped[str | None] = mapped_column(Text, nullable=True)
    previous_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    changed: Mapped[bool] = mapped_column(Boolean, default=False)
    alert_triggered: Mapped[bool] = mapped_column(Boolean, default=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    monitor: Mapped[Monitor] = relationship(back_populates="runs")
    snapshot: Mapped[Snapshot | None] = relationship(back_populates="run", uselist=False, cascade="all, delete-orphan")
    notifications: Mapped[list[Notification]] = relationship(back_populates="run", cascade="all, delete-orphan")


class Snapshot(Base):
    __tablename__ = "snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    monitor_id: Mapped[int] = mapped_column(ForeignKey("monitors.id", ondelete="CASCADE"), index=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("runs.id", ondelete="CASCADE"), unique=True)
    value: Mapped[str] = mapped_column(Text)
    content_hash: Mapped[str] = mapped_column(String(64), index=True)
    raw_excerpt: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    monitor: Mapped[Monitor] = relationship(back_populates="snapshots")
    run: Mapped[Run] = relationship(back_populates="snapshot")


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    monitor_id: Mapped[int] = mapped_column(ForeignKey("monitors.id", ondelete="CASCADE"), index=True)
    run_id: Mapped[int | None] = mapped_column(ForeignKey("runs.id", ondelete="SET NULL"), nullable=True)
    channel: Mapped[str] = mapped_column(String(30), default="in_app")
    status: Mapped[str] = mapped_column(String(30), default="sent")
    title: Mapped[str] = mapped_column(String(255))
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    monitor: Mapped[Monitor] = relationship(back_populates="notifications")
    run: Mapped[Run | None] = relationship(back_populates="notifications")
