from __future__ import annotations

from marshmallow import Schema, ValidationError, fields, post_load, validate, validates_schema


PLAN_CHOICES = ["free", "pro", "enterprise"]
SYNC_STATUS_CHOICES = ["pending", "running", "succeeded", "failed", "cancelled"]
TRIGGER_CHOICES = ["manual", "scheduled", "webhook"]
EVENT_CHOICES = ["sync.completed", "sync.failed", "workspace.suspended"]
SOURCE_CHOICES = ["http_poll", "webhook_push", "file_watch", "database_cdc"]
PRIORITY_CHOICES = ["low", "normal", "high", "critical"]


class SettingsBlockSchema(Schema):
    """Implements SettingsBlock; marshmallow Schema object — defined separately from data classes. This is Lane A: schema objects are explicit, not derived from type annotations."""

    retry_max = fields.Int(required=True, validate=validate.Range(min=0, max=10))
    timeout_seconds = fields.Int(required=True, validate=validate.Range(min=10, max=3600))
    notify_on_failure = fields.Bool(required=True)
    webhook_url = fields.Url(allow_none=True, load_default=None)

    @post_load
    def to_dict(self, data, **kwargs):  # type: ignore[no-untyped-def]
        return dict(data)


class WorkspaceConfigSchema(Schema):
    """Implements WorkspaceConfig; marshmallow Schema object — defined separately from data classes. This is Lane A: schema objects are explicit, not derived from type annotations."""

    id = fields.UUID(required=True)
    name = fields.Str(required=True, validate=validate.Length(min=3, max=100))
    slug = fields.Str(required=True, validate=validate.Regexp(r"^[a-z][a-z0-9-]{1,48}[a-z0-9]$"))
    owner_email = fields.Email(required=True)
    plan = fields.Str(required=True, validate=validate.OneOf(PLAN_CHOICES))
    max_sync_runs = fields.Int(required=True, validate=validate.Range(min=1, max=1000))
    settings = fields.Nested(SettingsBlockSchema, required=True)
    tags = fields.List(
        fields.Str(validate=validate.Length(min=1, max=50)),
        required=True,
        validate=validate.Length(max=20),
    )
    created_at = fields.DateTime(required=True, format="iso")
    suspended_until = fields.DateTime(format="iso", allow_none=True, load_default=None)

    @validates_schema
    def validate_plan_limit(self, data, **kwargs):  # type: ignore[no-untyped-def]
        plan = data.get("plan")
        max_sync_runs = data.get("max_sync_runs")
        if plan == "free" and max_sync_runs and max_sync_runs > 10:
            raise ValidationError("free plan supports at most 10 sync runs", "max_sync_runs")
        if plan == "pro" and max_sync_runs and max_sync_runs > 100:
            raise ValidationError("pro plan supports at most 100 sync runs", "max_sync_runs")


class SyncRunSchema(Schema):
    """Implements SyncRun; marshmallow Schema object — defined separately from data classes. This is Lane A: schema objects are explicit, not derived from type annotations."""

    run_id = fields.UUID(required=True)
    workspace_id = fields.UUID(required=True)
    status = fields.Str(required=True, validate=validate.OneOf(SYNC_STATUS_CHOICES))
    trigger = fields.Str(required=True, validate=validate.OneOf(TRIGGER_CHOICES))
    started_at = fields.DateTime(format="iso", allow_none=True, load_default=None)
    finished_at = fields.DateTime(format="iso", allow_none=True, load_default=None)
    duration_ms = fields.Int(allow_none=True, load_default=None, validate=validate.Range(min=0))
    records_ingested = fields.Int(
        allow_none=True,
        load_default=None,
        validate=validate.Range(min=0, max=10_000_000),
    )
    error_code = fields.Str(allow_none=True, load_default=None)

    @validates_schema
    def validate_sync_run(self, data, **kwargs):  # type: ignore[no-untyped-def]
        started_at = data.get("started_at")
        finished_at = data.get("finished_at")
        duration_ms = data.get("duration_ms")
        status = data.get("status")
        error_code = data.get("error_code")
        if finished_at is not None and started_at is None:
            raise ValidationError("finished_at requires started_at", "finished_at")
        if started_at is not None and finished_at is not None and finished_at < started_at:
            raise ValidationError("finished_at must be >= started_at", "finished_at")
        if finished_at is not None and duration_ms is None:
            raise ValidationError("duration_ms is required when finished_at is present", "duration_ms")
        if status == "failed" and not error_code:
            raise ValidationError("failed sync runs require error_code", "error_code")
        if status != "failed" and error_code is not None:
            raise ValidationError("error_code must be null unless status is failed", "error_code")


class SyncCompletedDataSchema(Schema):
    duration_ms = fields.Int(required=True, validate=validate.Range(min=0))
    records_ingested = fields.Int(required=True, validate=validate.Range(min=0, max=10_000_000))
    run_id = fields.UUID(required=True)
    workspace_id = fields.UUID(required=True)


class SyncFailedDataSchema(Schema):
    run_id = fields.UUID(required=True)
    workspace_id = fields.UUID(required=True)
    error_code = fields.Str(required=True, validate=validate.Length(min=1))
    error_message = fields.Str(required=True, validate=validate.Length(min=1, max=500))


class WorkspaceSuspendedDataSchema(Schema):
    workspace_id = fields.UUID(required=True)
    suspended_until = fields.DateTime(required=True, format="iso")
    reason = fields.Str(required=True, validate=validate.OneOf(["policy_violation", "payment_failure", "manual"]))


class WebhookPayloadSchema(Schema):
    """Implements WebhookPayload; marshmallow Schema object — defined separately from data classes. This is Lane A: schema objects are explicit, not derived from type annotations."""

    event_type = fields.Str(required=True, validate=validate.OneOf(EVENT_CHOICES))
    payload_version = fields.Str(required=True, validate=validate.OneOf(["v1", "v2", "v3"]))
    timestamp = fields.DateTime(required=True, format="iso")
    signature = fields.Str(required=True, validate=validate.Regexp(r"^[a-f0-9]{64}$"))
    data = fields.Dict(required=True)

    @validates_schema
    def validate_event_payload(self, data, **kwargs):  # type: ignore[no-untyped-def]
        # marshmallow has no native discriminated-union field, so this example
        # dispatches to a sub-schema manually using the envelope event_type.
        schema_map = {
            "sync.completed": SyncCompletedDataSchema(),
            "sync.failed": SyncFailedDataSchema(),
            "workspace.suspended": WorkspaceSuspendedDataSchema(),
        }
        schema = schema_map[data["event_type"]]
        data["data"] = schema.load(data["data"])


class HttpPollConfigSchema(Schema):
    url = fields.Url(required=True)
    method = fields.Str(required=True, validate=validate.OneOf(["GET", "POST"]))
    headers = fields.Dict(
        keys=fields.Str(),
        values=fields.Str(),
        required=True,
        validate=validate.Length(max=20),
    )


class WebhookPushConfigSchema(Schema):
    path = fields.Str(required=True, validate=validate.Regexp(r"^/"))
    secret = fields.Str(required=True, validate=validate.Length(min=1))


class FileWatchConfigSchema(Schema):
    path = fields.Str(required=True, validate=validate.Length(min=1))
    pattern = fields.Str(required=True, validate=validate.Length(min=1))


class DatabaseCdcConfigSchema(Schema):
    dsn = fields.Str(required=True, validate=validate.Length(min=1))
    table = fields.Str(required=True, validate=validate.Length(min=1))
    cursor_field = fields.Str(required=True, validate=validate.Length(min=1))


class IngestionSourceSchema(Schema):
    """Implements IngestionSource; marshmallow Schema object — defined separately from data classes. This is Lane A: schema objects are explicit, not derived from type annotations."""

    source_id = fields.UUID(required=True)
    source_type = fields.Str(required=True, validate=validate.OneOf(SOURCE_CHOICES))
    config = fields.Dict(required=True)
    enabled = fields.Bool(required=True)
    poll_interval_seconds = fields.Int(
        allow_none=True,
        load_default=None,
        validate=validate.Range(min=60),
    )

    @validates_schema
    def validate_source(self, data, **kwargs):  # type: ignore[no-untyped-def]
        schema_map = {
            "http_poll": HttpPollConfigSchema(),
            "webhook_push": WebhookPushConfigSchema(),
            "file_watch": FileWatchConfigSchema(),
            "database_cdc": DatabaseCdcConfigSchema(),
        }
        data["config"] = schema_map[data["source_type"]].load(data["config"])
        poll_interval = data.get("poll_interval_seconds")
        if data["source_type"] == "http_poll":
            if poll_interval is None:
                raise ValidationError("http_poll sources require poll_interval_seconds", "poll_interval_seconds")
        elif poll_interval is not None:
            raise ValidationError("poll_interval_seconds must be null for non-http_poll sources", "poll_interval_seconds")


class ReviewRequestSchema(Schema):
    """Implements ReviewRequest; marshmallow Schema object — defined separately from data classes. This is Lane A: schema objects are explicit, not derived from type annotations."""

    request_id = fields.UUID(required=True)
    workspace_id = fields.UUID(required=True)
    reviewer_emails = fields.List(
        fields.Email(),
        required=True,
        validate=validate.Length(min=1, max=5),
    )
    content_ids = fields.List(
        fields.UUID(),
        required=True,
        validate=validate.Length(min=1, max=50),
    )
    priority = fields.Str(required=True, validate=validate.OneOf(PRIORITY_CHOICES))
    due_at = fields.DateTime(format="iso", allow_none=True, load_default=None)
    notes = fields.Str(allow_none=True, load_default=None, validate=validate.Length(max=2000))

    @validates_schema
    def validate_review_request(self, data, **kwargs):  # type: ignore[no-untyped-def]
        reviewer_emails = data.get("reviewer_emails", [])
        content_ids = [str(value) for value in data.get("content_ids", [])]
        if len(set(reviewer_emails)) != len(reviewer_emails):
            raise ValidationError("reviewer_emails must be unique", "reviewer_emails")
        if len(set(content_ids)) != len(content_ids):
            raise ValidationError("content_ids must be unique", "content_ids")
        if data.get("priority") == "critical" and data.get("due_at") is None:
            raise ValidationError("critical review requests require due_at", "due_at")
