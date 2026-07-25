from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models import ConditionType, ExtractionType, RunStatus


class UserCreate(BaseModel):
    email: str
    password: str = Field(min_length=8, max_length=128)
    display_name: str = Field(default="Usuário", min_length=2, max_length=120)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        value = value.strip().lower()
        if "@" not in value or value.startswith("@") or value.endswith("@"):
            raise ValueError("E-mail inválido")
        return value


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    display_name: str
    is_active: bool
    created_at: datetime


class MonitorBase(BaseModel):
    name: str = Field(min_length=2, max_length=180)
    description: str | None = Field(default=None, max_length=1000)
    url: str = Field(min_length=8, max_length=3000)
    selector: str | None = Field(default=None, max_length=500)
    extraction_type: ExtractionType = ExtractionType.TEXT
    attribute_name: str | None = Field(default=None, max_length=120)
    render_js: bool = False
    interval_minutes: int = Field(default=30, ge=1, le=43_200)
    condition_type: ConditionType = ConditionType.ANY_CHANGE
    threshold: float | None = None
    keyword: str | None = Field(default=None, max_length=255)
    is_active: bool = True


class MonitorCreate(MonitorBase):
    pass


class MonitorUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=180)
    description: str | None = Field(default=None, max_length=1000)
    url: str | None = Field(default=None, min_length=8, max_length=3000)
    selector: str | None = Field(default=None, max_length=500)
    extraction_type: ExtractionType | None = None
    attribute_name: str | None = Field(default=None, max_length=120)
    render_js: bool | None = None
    interval_minutes: int | None = Field(default=None, ge=1, le=43_200)
    condition_type: ConditionType | None = None
    threshold: float | None = None
    keyword: str | None = Field(default=None, max_length=255)
    is_active: bool | None = None


class MonitorOut(MonitorBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    last_value: str | None
    last_hash: str | None
    last_checked_at: datetime | None
    next_run_at: datetime | None
    created_at: datetime
    updated_at: datetime


class RunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    monitor_id: int
    status: RunStatus
    started_at: datetime | None
    finished_at: datetime | None
    http_status: int | None
    duration_ms: int | None
    attempts: int
    value: str | None
    previous_value: str | None
    changed: bool
    alert_triggered: bool
    error_message: str | None
    created_at: datetime


class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    monitor_id: int
    run_id: int | None
    channel: str
    status: str
    title: str
    body: str
    created_at: datetime


class DashboardSummary(BaseModel):
    total_monitors: int
    active_monitors: int
    total_runs: int
    successful_runs: int
    changed_runs: int
    failed_runs: int
    unread_notifications: int
    success_rate: float
    average_duration_ms: int
    recent_runs: list[RunOut]
    recent_notifications: list[NotificationOut]


class RunQueued(BaseModel):
    run_id: int
    status: str
    execution_mode: str


class HealthResponse(BaseModel):
    status: str
    app: str
    version: str
    database: str
