// Package validate demonstrates ozzo-validation's code-driven style.
//
// ozzo-validation: all rules are in code, not struct tags. Cross-field rules
// are expressed as explicit if-statements, making them easy to read and test.
// The Validate() method returns validation.Errors - a map of field name to
// error. This is Lane A with code-driven rule composition.
package validate

import (
	"encoding/json"
	"fmt"
	"regexp"
	"strings"

	validation "github.com/go-ozzo/ozzo-validation/v4"
	"github.com/go-ozzo/ozzo-validation/v4/is"

	"workspace-sync-validator-ozzo/models"
)

var (
	slugPattern  = regexp.MustCompile(`^[a-z][a-z0-9-]{1,48}[a-z0-9]$`)
	hex64Pattern = regexp.MustCompile(`^[a-f0-9]{64}$`)
)

func ValidateWorkspaceConfig(w *models.WorkspaceConfig) error {
	errs := validation.Errors{}
	baseErr := validation.ValidateStruct(w,
		validation.Field(&w.ID, validation.Required, is.UUID),
		validation.Field(&w.Name, validation.Required, validation.Length(3, 100)),
		validation.Field(&w.Slug, validation.Required, validation.Match(slugPattern)),
		validation.Field(&w.OwnerEmail, validation.Required, is.Email),
		validation.Field(&w.Plan, validation.Required, validation.In(models.PlanFree, models.PlanPro, models.PlanEnterprise)),
		validation.Field(&w.MaxSyncRuns, validation.Required, validation.Min(1), validation.Max(1000)),
		validation.Field(&w.Settings, validation.By(func(value interface{}) error {
			settings := value.(models.SettingsBlock)
			return validation.ValidateStruct(&settings,
				validation.Field(&settings.RetryMax, validation.Min(0), validation.Max(10)),
				validation.Field(&settings.TimeoutSeconds, validation.Required, validation.Min(10), validation.Max(3600)),
				validation.Field(&settings.WebhookURL, validation.NilOrNotEmpty, is.URL),
			)
		})),
		validation.Field(&w.Tags, validation.Length(0, 20)),
	)
	if baseErr != nil {
		errs["base"] = baseErr
	}
	for idx, tag := range w.Tags {
		if err := validation.Validate(tag, validation.Length(1, 50)); err != nil {
			errs[fmt.Sprintf("tags[%d]", idx)] = err
		}
	}
	switch w.Plan {
	case models.PlanFree:
		if w.MaxSyncRuns > 10 {
			errs["max_sync_runs"] = validation.NewError("plan_limit", "must be <= 10 for free plan")
		}
	case models.PlanPro:
		if w.MaxSyncRuns > 100 {
			errs["max_sync_runs"] = validation.NewError("plan_limit", "must be <= 100 for pro plan")
		}
	}
	if len(errs) == 0 {
		return nil
	}
	return errs
}

func ValidateSyncRun(s *models.SyncRun) error {
	errs := validation.Errors{}
	if err := validation.ValidateStruct(s,
		validation.Field(&s.RunID, validation.Required, is.UUID),
		validation.Field(&s.WorkspaceID, validation.Required, is.UUID),
		validation.Field(&s.Status, validation.Required, validation.In(models.SyncPending, models.SyncRunning, models.SyncSucceeded, models.SyncFailed, models.SyncCancelled)),
		validation.Field(&s.Trigger, validation.Required, validation.In(models.TriggerManual, models.TriggerScheduled, models.TriggerWebhook)),
		validation.Field(&s.DurationMs, validation.NilOrNotEmpty, validation.Min(int64(0))),
		validation.Field(&s.RecordsIngested, validation.NilOrNotEmpty, validation.Min(int64(0)), validation.Max(int64(10000000))),
	); err != nil {
		errs["base"] = err
	}
	if s.FinishedAt != nil && s.StartedAt == nil {
		errs["started_at"] = validation.NewError("required", "is required when finished_at is set")
	}
	if s.StartedAt != nil && s.FinishedAt != nil && s.FinishedAt.Before(*s.StartedAt) {
		errs["finished_at"] = validation.NewError("order", "must be >= started_at")
	}
	if s.FinishedAt != nil && s.DurationMs == nil {
		errs["duration_ms"] = validation.NewError("required", "is required when finished_at is set")
	}
	if s.Status == models.SyncFailed && s.ErrorCode == nil {
		errs["error_code"] = validation.NewError("required", "is required when status is failed")
	}
	if s.Status != models.SyncFailed && s.ErrorCode != nil {
		errs["error_code"] = validation.NewError("unexpected", "must be null unless status is failed")
	}
	if len(errs) == 0 {
		return nil
	}
	return errs
}

func ValidateWebhookPayload(p *models.WebhookPayload) error {
	errs := validation.Errors{}
	if err := validation.ValidateStruct(p,
		validation.Field(&p.EventType, validation.Required, validation.In(models.WebhookSyncCompleted, models.WebhookSyncFailed, models.WebhookSuspended)),
		validation.Field(&p.PayloadVersion, validation.Required, validation.In("v1", "v2", "v3")),
		validation.Field(&p.Signature, validation.Required, validation.Match(hex64Pattern)),
	); err != nil {
		errs["base"] = err
	}
	switch p.EventType {
	case models.WebhookSyncCompleted:
		var data models.SyncCompletedData
		if err := json.Unmarshal(p.Data, &data); err != nil {
			errs["data"] = err
			break
		}
		if err := validation.ValidateStruct(&data,
			validation.Field(&data.RunID, validation.Required, is.UUID),
			validation.Field(&data.WorkspaceID, validation.Required, is.UUID),
			validation.Field(&data.DurationMs, validation.Min(int64(0))),
			validation.Field(&data.RecordsIngested, validation.Min(int64(0)), validation.Max(int64(10000000))),
		); err != nil {
			errs["data"] = err
		}
	case models.WebhookSyncFailed:
		var data models.SyncFailedData
		if err := json.Unmarshal(p.Data, &data); err != nil {
			errs["data"] = err
			break
		}
		if err := validation.ValidateStruct(&data,
			validation.Field(&data.RunID, validation.Required, is.UUID),
			validation.Field(&data.WorkspaceID, validation.Required, is.UUID),
			validation.Field(&data.ErrorCode, validation.Required, validation.Length(1, 100)),
			validation.Field(&data.ErrorMessage, validation.Required, validation.Length(1, 500)),
		); err != nil {
			errs["data"] = err
		}
	case models.WebhookSuspended:
		var data models.WorkspaceSuspendedData
		if err := json.Unmarshal(p.Data, &data); err != nil {
			errs["data"] = err
			break
		}
		if err := validation.ValidateStruct(&data,
			validation.Field(&data.WorkspaceID, validation.Required, is.UUID),
			validation.Field(&data.Reason, validation.Required, validation.In(models.ReasonPolicyViolation, models.ReasonPaymentFailure, models.ReasonManual)),
		); err != nil {
			errs["data"] = err
		}
	}
	if len(errs) == 0 {
		return nil
	}
	return errs
}

func ValidateIngestionSource(src *models.IngestionSource) error {
	errs := validation.Errors{}
	if err := validation.ValidateStruct(src,
		validation.Field(&src.SourceID, validation.Required, is.UUID),
		validation.Field(&src.SourceType, validation.Required, validation.In(models.SourceHTTPPoll, models.SourceWebhook, models.SourceFileWatch, models.SourceDatabaseCD)),
	); err != nil {
		errs["base"] = err
	}
	switch src.SourceType {
	case models.SourceHTTPPoll:
		var cfg models.HttpPollConfig
		if err := json.Unmarshal(src.Config, &cfg); err != nil {
			errs["config"] = err
			break
		}
		if err := validation.ValidateStruct(&cfg,
			validation.Field(&cfg.URL, validation.Required, is.URL),
			validation.Field(&cfg.Method, validation.Required, validation.In(models.MethodGET, models.MethodPOST)),
		); err != nil {
			errs["config"] = err
		}
		if src.PollIntervalSeconds == nil || *src.PollIntervalSeconds < 60 {
			errs["poll_interval_seconds"] = validation.NewError("required", "must be present and >= 60 for http_poll")
		}
	default:
		if src.PollIntervalSeconds != nil {
			errs["poll_interval_seconds"] = validation.NewError("unexpected", "must be null unless source_type is http_poll")
		}
	}
	if len(errs) == 0 {
		return nil
	}
	return errs
}

func ValidateReviewRequest(req *models.ReviewRequest) error {
	errs := validation.Errors{}
	if err := validation.ValidateStruct(req,
		validation.Field(&req.RequestID, validation.Required, is.UUID),
		validation.Field(&req.WorkspaceID, validation.Required, is.UUID),
		validation.Field(&req.ReviewerEmails, validation.Required, validation.Length(1, 5)),
		validation.Field(&req.ContentIDs, validation.Required, validation.Length(1, 50)),
		validation.Field(&req.Priority, validation.Required, validation.In(models.PriorityLow, models.PriorityNormal, models.PriorityHigh, models.PriorityCritical)),
		validation.Field(&req.Notes, validation.NilOrNotEmpty, validation.Length(0, 2000)),
	); err != nil {
		errs["base"] = err
	}
	if req.Priority == models.PriorityCritical && req.DueAt == nil {
		errs["due_at"] = validation.NewError("required", "is required when priority is critical")
	}
	seenReviewers := map[string]struct{}{}
	for _, reviewer := range req.ReviewerEmails {
		if err := validation.Validate(reviewer, validation.Required, is.Email); err != nil {
			errs["reviewer_emails"] = err
			break
		}
		key := strings.ToLower(reviewer)
		if _, exists := seenReviewers[key]; exists {
			errs["reviewer_emails"] = validation.NewError("duplicate", "must not contain duplicates")
			break
		}
		seenReviewers[key] = struct{}{}
	}
	seenContent := map[string]struct{}{}
	for _, id := range req.ContentIDs {
		if err := validation.Validate(id, validation.Required, is.UUID); err != nil {
			errs["content_ids"] = err
			break
		}
		if _, exists := seenContent[id]; exists {
			errs["content_ids"] = validation.NewError("duplicate", "must not contain duplicates")
			break
		}
		seenContent[id] = struct{}{}
	}
	if len(errs) == 0 {
		return nil
	}
	return errs
}
