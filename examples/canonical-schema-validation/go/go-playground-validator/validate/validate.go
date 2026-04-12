// Package validate implements go-playground/validator checks for the
// WorkspaceSyncContext example.
//
// go-playground/validator uses struct tags for field-level rules (Lane A,
// tag-based). Cross-field rules and discriminated union dispatch require
// explicit code in this package - tags alone are insufficient for the
// WorkspaceSyncContext domain. This is a characteristic limitation of the
// tag-based approach.
package validate

import (
	"encoding/json"
	"fmt"
	"regexp"
	"strings"

	"github.com/go-playground/validator/v10"

	"workspace-sync-validator-go-playground/models"
)

var (
	slugPattern  = regexp.MustCompile(`^[a-z][a-z0-9-]{1,48}[a-z0-9]$`)
	hex64Pattern = regexp.MustCompile(`^[a-f0-9]{64}$`)
)

var validate = newValidator()

func newValidator() *validator.Validate {
	v := validator.New()
	_ = v.RegisterValidation("slug_format", func(fl validator.FieldLevel) bool {
		return slugPattern.MatchString(fl.Field().String())
	})
	_ = v.RegisterValidation("hex64", func(fl validator.FieldLevel) bool {
		return hex64Pattern.MatchString(fl.Field().String())
	})
	return v
}

func combineErrs(errs ...error) error {
	parts := make([]string, 0, len(errs))
	for _, err := range errs {
		if err == nil {
			continue
		}
		parts = append(parts, err.Error())
	}
	if len(parts) == 0 {
		return nil
	}
	return fmt.Errorf(strings.Join(parts, "; "))
}

func ValidateWorkspaceConfig(cfg *models.WorkspaceConfig) error {
	structErr := validate.Struct(cfg)
	var crossFieldErr error
	switch cfg.Plan {
	case models.PlanFree:
		if cfg.MaxSyncRuns > 10 {
			crossFieldErr = fmt.Errorf("max_sync_runs must be <= 10 for free plan")
		}
	case models.PlanPro:
		if cfg.MaxSyncRuns > 100 {
			crossFieldErr = fmt.Errorf("max_sync_runs must be <= 100 for pro plan")
		}
	}
	return combineErrs(structErr, crossFieldErr)
}

func ValidateSyncRun(run *models.SyncRun) error {
	structErr := validate.Struct(run)
	var checks []error
	if run.FinishedAt != nil && run.StartedAt == nil {
		checks = append(checks, fmt.Errorf("started_at is required when finished_at is set"))
	}
	if run.FinishedAt != nil && run.StartedAt != nil && run.FinishedAt.Before(*run.StartedAt) {
		checks = append(checks, fmt.Errorf("finished_at must be >= started_at"))
	}
	if run.FinishedAt != nil && run.DurationMs == nil {
		checks = append(checks, fmt.Errorf("duration_ms is required when finished_at is set"))
	}
	if run.Status == models.SyncFailed && run.ErrorCode == nil {
		checks = append(checks, fmt.Errorf("error_code is required when status is failed"))
	}
	if run.Status != models.SyncFailed && run.ErrorCode != nil {
		checks = append(checks, fmt.Errorf("error_code must be null unless status is failed"))
	}
	args := []error{structErr}
	args = append(args, checks...)
	return combineErrs(args...)
}

func ValidateWebhookPayload(p *models.WebhookPayload) (interface{}, error) {
	if err := validate.Struct(p); err != nil {
		return nil, err
	}

	switch p.EventType {
	case models.WebhookSyncCompleted:
		var data models.SyncCompletedData
		if err := json.Unmarshal(p.Data, &data); err != nil {
			return nil, err
		}
		return &data, validate.Struct(&data)
	case models.WebhookSyncFailed:
		var data models.SyncFailedData
		if err := json.Unmarshal(p.Data, &data); err != nil {
			return nil, err
		}
		return &data, validate.Struct(&data)
	case models.WebhookWorkspaceStopped:
		var data models.WorkspaceSuspendedData
		if err := json.Unmarshal(p.Data, &data); err != nil {
			return nil, err
		}
		return &data, validate.Struct(&data)
	default:
		return nil, fmt.Errorf("unsupported event_type %q", p.EventType)
	}
}

func ValidateIngestionSource(src *models.IngestionSource) error {
	if err := validate.Struct(src); err != nil {
		return err
	}
	switch src.SourceType {
	case models.SourceHTTPPoll:
		var cfg models.HttpPollConfig
		if err := json.Unmarshal(src.Config, &cfg); err != nil {
			return err
		}
		if err := validate.Struct(&cfg); err != nil {
			return err
		}
		if src.PollIntervalSeconds == nil || *src.PollIntervalSeconds < 60 {
			return fmt.Errorf("poll_interval_seconds is required and must be >= 60 for http_poll")
		}
	case models.SourceWebhook:
		var cfg models.WebhookPushConfig
		if err := json.Unmarshal(src.Config, &cfg); err != nil {
			return err
		}
		if err := validate.Struct(&cfg); err != nil {
			return err
		}
		if src.PollIntervalSeconds != nil {
			return fmt.Errorf("poll_interval_seconds must be null for non-http_poll sources")
		}
	case models.SourceFileWatch:
		var cfg models.FileWatchConfig
		if err := json.Unmarshal(src.Config, &cfg); err != nil {
			return err
		}
		if err := validate.Struct(&cfg); err != nil {
			return err
		}
		if src.PollIntervalSeconds != nil {
			return fmt.Errorf("poll_interval_seconds must be null for non-http_poll sources")
		}
	case models.SourceDatabaseCD:
		var cfg models.DatabaseCDCConfig
		if err := json.Unmarshal(src.Config, &cfg); err != nil {
			return err
		}
		if err := validate.Struct(&cfg); err != nil {
			return err
		}
		if src.PollIntervalSeconds != nil {
			return fmt.Errorf("poll_interval_seconds must be null for non-http_poll sources")
		}
	}
	return nil
}

func ValidateReviewRequest(req *models.ReviewRequest) error {
	structErr := validate.Struct(req)
	seenReviewers := map[string]struct{}{}
	seenContent := map[string]struct{}{}
	var checks []error
	if req.Priority == models.PriorityCritical && req.DueAt == nil {
		checks = append(checks, fmt.Errorf("due_at is required when priority is critical"))
	}
	for _, reviewer := range req.ReviewerEmails {
		if _, exists := seenReviewers[reviewer]; exists {
			checks = append(checks, fmt.Errorf("reviewer_emails must not contain duplicates"))
			break
		}
		seenReviewers[reviewer] = struct{}{}
	}
	for _, id := range req.ContentIDs {
		if _, exists := seenContent[id]; exists {
			checks = append(checks, fmt.Errorf("content_ids must not contain duplicates"))
			break
		}
		seenContent[id] = struct{}{}
	}
	args := []error{structErr}
	args = append(args, checks...)
	return combineErrs(args...)
}
