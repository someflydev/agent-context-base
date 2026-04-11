from __future__ import annotations

from datetime import datetime
from enum import Enum
import re
from typing import Any
from urllib.parse import urlparse
from uuid import UUID

from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
SLUG_RE = re.compile(r"^[a-z][a-z0-9-]{1,48}[a-z0-9]$")
HEX64_RE = re.compile(r"^[a-f0-9]{64}$")


def _validate_email(value: str) -> str:
    if not EMAIL_RE.fullmatch(value):
        raise ValueError("must be a valid email address")
    return value


def _validate_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("must be a valid http/https URL")
    return value


class PlanEnum(str, Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class SyncStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TriggerType(str, Enum):
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    WEBHOOK = "webhook"


class WebhookEventType(str, Enum):
    SYNC_COMPLETED = "sync.completed"
    SYNC_FAILED = "sync.failed"
    WORKSPACE_SUSPENDED = "workspace.suspended"


class SuspensionReason(str, Enum):
    POLICY_VIOLATION = "policy_violation"
    PAYMENT_FAILURE = "payment_failure"
    MANUAL = "manual"


class SourceType(str, Enum):
    HTTP_POLL = "http_poll"
    WEBHOOK_PUSH = "webhook_push"
    FILE_WATCH = "file_watch"
    DATABASE_CDC = "database_cdc"


class HttpMethod(str, Enum):
    GET = "GET"
    POST = "POST"


class ReviewPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class SettingsBlock(BaseModel):
    """Implements SettingsBlock; Lane C uses one BaseModel as type, validator, and schema source."""

    retry_max: int = Field(ge=0, le=10)
    timeout_seconds: int = Field(ge=10, le=3600)
    notify_on_failure: bool
    webhook_url: str | None = None

    @field_validator("webhook_url")
    @classmethod
    def validate_webhook_url(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return _validate_url(value)


class WorkspaceConfig(BaseModel):
    """Implements WorkspaceConfig; Lane C uses one BaseModel as type, validator, and schema source."""

    id: UUID
    name: str = Field(min_length=3, max_length=100)
    slug: str
    owner_email: str
    plan: PlanEnum
    max_sync_runs: int = Field(ge=1, le=1000)
    settings: SettingsBlock
    tags: list[str] = Field(max_length=20)
    created_at: datetime = Field(...)
    suspended_until: datetime | None = None

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, value: str) -> str:
        if not SLUG_RE.fullmatch(value):
            raise ValueError("must match the canonical workspace slug pattern")
        return value

    @field_validator("owner_email")
    @classmethod
    def validate_owner_email(cls, value: str) -> str:
        return _validate_email(value)

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, values: list[str]) -> list[str]:
        for tag in values:
            if not 1 <= len(tag) <= 50:
                raise ValueError("each tag must be between 1 and 50 characters")
        return values

    @model_validator(mode="after")
    def validate_plan_limit(self) -> "WorkspaceConfig":
        if self.plan == PlanEnum.FREE and self.max_sync_runs > 10:
            raise ValueError("free plan supports at most 10 sync runs")
        if self.plan == PlanEnum.PRO and self.max_sync_runs > 100:
            raise ValueError("pro plan supports at most 100 sync runs")
        # Known limitation: the shared domain marks created_at as not future-dated,
        # but this example does not add clock-relative validation.
        return self


class SyncRun(BaseModel):
    """Implements SyncRun; Lane C uses one BaseModel as type, validator, and schema source."""

    run_id: UUID
    workspace_id: UUID
    status: SyncStatus
    trigger: TriggerType
    started_at: datetime | None = None
    finished_at: datetime | None = None
    duration_ms: int | None = Field(default=None, ge=0)
    records_ingested: int | None = Field(default=None, ge=0, le=10_000_000)
    error_code: str | None = None

    @model_validator(mode="after")
    def validate_timeline(self) -> "SyncRun":
        if self.finished_at is not None and self.started_at is None:
            raise ValueError("finished_at requires started_at")
        if self.started_at and self.finished_at and self.finished_at < self.started_at:
            raise ValueError("finished_at must be greater than or equal to started_at")
        if self.finished_at is not None and self.duration_ms is None:
            raise ValueError("duration_ms is required when finished_at is present")
        if self.status == SyncStatus.FAILED and not self.error_code:
            raise ValueError("failed sync runs require error_code")
        if self.status != SyncStatus.FAILED and self.error_code is not None:
            raise ValueError("error_code must be null unless status is failed")
        return self


class SyncCompletedData(BaseModel):
    """Implements WebhookPayload.sync.completed data; Lane C keeps model, validation, and schema unified."""

    run_id: UUID
    workspace_id: UUID
    duration_ms: int = Field(ge=0)
    records_ingested: int = Field(ge=0, le=10_000_000)


class SyncFailedData(BaseModel):
    """Implements WebhookPayload.sync.failed data; Lane C keeps model, validation, and schema unified."""

    run_id: UUID
    workspace_id: UUID
    error_code: str = Field(min_length=1)
    error_message: str = Field(min_length=1, max_length=500)


class WorkspaceSuspendedData(BaseModel):
    """Implements WebhookPayload.workspace.suspended data; Lane C keeps model, validation, and schema unified."""

    workspace_id: UUID
    suspended_until: datetime
    reason: SuspensionReason


class WebhookPayload(BaseModel):
    """Implements WebhookPayload; Lane C uses one BaseModel as type, validator, and schema source."""

    event_type: WebhookEventType
    payload_version: str = Field(pattern=r"^v[123]$")
    timestamp: datetime
    signature: str
    data: SyncCompletedData | SyncFailedData | WorkspaceSuspendedData

    @field_validator("signature")
    @classmethod
    def validate_signature(cls, value: str) -> str:
        if not HEX64_RE.fullmatch(value):
            raise ValueError("signature must be exactly 64 lowercase hex characters")
        return value

    @model_validator(mode="before")
    @classmethod
    def dispatch_payload_data(cls, values: Any) -> Any:
        if not isinstance(values, dict):
            return values
        event_type = values.get("event_type")
        data = values.get("data")
        if not isinstance(data, dict):
            return values
        # The shared fixture corpus keeps the discriminator on the outer envelope,
        # so we dispatch manually instead of relying on a nested discriminated union.
        model_map = {
            WebhookEventType.SYNC_COMPLETED.value: SyncCompletedData,
            WebhookEventType.SYNC_FAILED.value: SyncFailedData,
            WebhookEventType.WORKSPACE_SUSPENDED.value: WorkspaceSuspendedData,
        }
        model = model_map.get(event_type)
        if model is not None:
            values["data"] = model.model_validate(data)
        return values


class HttpPollConfig(BaseModel):
    """Implements IngestionSource.http_poll config; Lane C keeps model, validation, and schema unified."""

    url: str
    method: HttpMethod
    headers: dict[str, str] = Field(default_factory=dict, max_length=20)

    @field_validator("url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        return _validate_url(value)


class WebhookPushConfig(BaseModel):
    """Implements IngestionSource.webhook_push config; Lane C keeps model, validation, and schema unified."""

    path: str = Field(pattern=r"^/")
    secret: str = Field(min_length=1)


class FileWatchConfig(BaseModel):
    """Implements IngestionSource.file_watch config; Lane C keeps model, validation, and schema unified."""

    path: str = Field(min_length=1)
    pattern: str = Field(min_length=1)


class DatabaseCdcConfig(BaseModel):
    """Implements IngestionSource.database_cdc config; Lane C keeps model, validation, and schema unified."""

    dsn: str = Field(min_length=1)
    table: str = Field(min_length=1)
    cursor_field: str = Field(min_length=1)


class IngestionSource(BaseModel):
    """Implements IngestionSource; Lane C uses one BaseModel as type, validator, and schema source."""

    source_id: UUID
    source_type: SourceType
    config: HttpPollConfig | WebhookPushConfig | FileWatchConfig | DatabaseCdcConfig
    enabled: bool
    poll_interval_seconds: int | None = None

    @model_validator(mode="before")
    @classmethod
    def dispatch_config(cls, values: Any) -> Any:
        if not isinstance(values, dict):
            return values
        source_type = values.get("source_type")
        config = values.get("config")
        if not isinstance(config, dict):
            return values
        model_map = {
            SourceType.HTTP_POLL.value: HttpPollConfig,
            SourceType.WEBHOOK_PUSH.value: WebhookPushConfig,
            SourceType.FILE_WATCH.value: FileWatchConfig,
            SourceType.DATABASE_CDC.value: DatabaseCdcConfig,
        }
        model = model_map.get(source_type)
        if model is not None:
            values["config"] = model.model_validate(config)
        return values

    @model_validator(mode="after")
    def validate_poll_interval(self) -> "IngestionSource":
        if self.source_type == SourceType.HTTP_POLL:
            if self.poll_interval_seconds is None or self.poll_interval_seconds < 60:
                raise ValueError("http_poll sources require poll_interval_seconds >= 60")
        elif self.poll_interval_seconds is not None:
            raise ValueError("poll_interval_seconds must be null for non-http_poll sources")
        return self


class ReviewRequest(BaseModel):
    """Implements ReviewRequest; Lane C uses one BaseModel as type, validator, and schema source."""

    request_id: UUID
    workspace_id: UUID
    reviewer_emails: list[str] = Field(min_length=1, max_length=5)
    content_ids: list[UUID] = Field(min_length=1, max_length=50)
    priority: ReviewPriority
    due_at: datetime | None = None
    notes: str | None = Field(default=None, max_length=2000)

    @field_validator("reviewer_emails")
    @classmethod
    def validate_reviewer_emails(cls, values: list[str]) -> list[str]:
        return [_validate_email(value) for value in values]

    @model_validator(mode="after")
    def validate_review_request(self) -> "ReviewRequest":
        if len(set(self.reviewer_emails)) != len(self.reviewer_emails):
            raise ValueError("reviewer_emails must be unique")
        content_ids = [str(content_id) for content_id in self.content_ids]
        if len(set(content_ids)) != len(content_ids):
            raise ValueError("content_ids must be unique")
        if self.priority == ReviewPriority.CRITICAL and self.due_at is None:
            raise ValueError("critical review requests require due_at")
        return self
