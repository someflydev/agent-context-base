@file:Suppress("MagicNumber")

/**
 * Konform validation DSL — rules defined in code using the Validation<T> { } block.
 * No annotations on data classes. This is Kotlin-idiomatic: explicit, composable,
 * null-safe. Cross-field rules use addConstraint with a predicate lambda.
 */
package validation

import io.konform.validation.Invalid
import io.konform.validation.Valid
import io.konform.validation.Validation
import io.konform.validation.ValidationResult
import io.konform.validation.constraints.maxItems
import io.konform.validation.constraints.maxLength
import io.konform.validation.constraints.maximum
import io.konform.validation.constraints.minLength
import io.konform.validation.constraints.minimum
import io.konform.validation.constraints.pattern
import models.IngestionSource
import models.PlanType
import models.ReviewPriority
import models.ReviewRequest
import models.SettingsBlock
import models.SourceType
import models.SyncRun
import models.SyncStatus
import models.SyncCompletedData
import models.SyncFailedData
import models.WebhookEventType
import models.WebhookPayload
import models.WorkspaceConfig
import models.WorkspaceSuspendedData

private val slugRegex = Regex("^[a-z][a-z0-9-]{1,48}[a-z0-9]$")
private val emailRegex = Regex(".+@.+\\..+")
private val urlRegex = Regex("^https?://.+")
private val hex64Regex = Regex("^[a-f0-9]{64}$")
private val payloadVersionRegex = Regex("^v[123]$")

val validateSettingsBlock = Validation<SettingsBlock> {
    SettingsBlock::retryMax {
        minimum(0)
        maximum(10)
    }
    SettingsBlock::timeoutSeconds {
        minimum(10)
        maximum(3600)
    }
    SettingsBlock::webhookUrl ifPresent {
        pattern(urlRegex, "must be a valid http/https URL")
    }
}

val validateWorkspaceConfig = Validation<WorkspaceConfig> {
    WorkspaceConfig::name {
        minLength(3)
        maxLength(100)
    }
    WorkspaceConfig::slug {
        pattern(slugRegex, "must be lowercase slug format")
    }
    WorkspaceConfig::ownerEmail {
        pattern(emailRegex, "must be a valid email")
    }
    WorkspaceConfig::maxSyncRuns {
        minimum(1)
        maximum(1000)
    }
    WorkspaceConfig::tags {
        maxItems(20)
    }
    WorkspaceConfig::settings {
        run(validateSettingsBlock)
    }
    addConstraint("each tag must be 1..50 chars") { config ->
        config.tags.all { it.length in 1..50 }
    }
}

val validateWorkspaceConfigCrossField = Validation<WorkspaceConfig> {
    addConstraint("maxSyncRuns must respect plan tier limits") { config ->
        when (config.plan) {
            PlanType.FREE -> config.maxSyncRuns <= 10
            PlanType.PRO -> config.maxSyncRuns <= 100
            PlanType.ENTERPRISE -> true
        }
    }
}

val validateSyncRun = Validation<SyncRun> {
    SyncRun::durationMs ifPresent {
        minimum(0L)
    }
    SyncRun::recordsIngested ifPresent {
        minimum(0L)
        maximum(10_000_000L)
    }
    addConstraint("finished_at requires started_at") { run ->
        run.finishedAt == null || run.startedAt != null
    }
    addConstraint("duration_ms is required when finished_at is set") { run ->
        run.finishedAt == null || run.durationMs != null
    }
    addConstraint("error_code is required only for failed runs") { run ->
        when (run.status) {
            SyncStatus.FAILED -> !run.errorCode.isNullOrBlank()
            else -> run.errorCode == null
        }
    }
    addConstraint("finished_at must not sort before started_at") { run ->
        if (run.startedAt == null || run.finishedAt == null) {
            true
        } else {
            run.finishedAt >= run.startedAt
        }
    }
}

val validateWebhookPayload = Validation<WebhookPayload> {
    WebhookPayload::payloadVersion {
        pattern(payloadVersionRegex, "must be v1, v2, or v3")
    }
    WebhookPayload::signature {
        pattern(hex64Regex, "must be exactly 64 lowercase hex characters")
    }
    addConstraint("data must match the event_type discriminant") { payload ->
        when (payload.eventType) {
            WebhookEventType.SYNC_COMPLETED -> payload.data is SyncCompletedData
            WebhookEventType.SYNC_FAILED -> payload.data is SyncFailedData
            WebhookEventType.WORKSPACE_SUSPENDED -> payload.data is WorkspaceSuspendedData
        }
    }
}

val validateReviewRequest = Validation<ReviewRequest> {
    ReviewRequest::notes ifPresent {
        maxLength(2000)
    }
    addConstraint("reviewer_emails must all be valid and unique") { request ->
        request.reviewerEmails.isNotEmpty() &&
            request.reviewerEmails.size <= 5 &&
            request.reviewerEmails.distinct().size == request.reviewerEmails.size &&
            request.reviewerEmails.all { emailRegex.matches(it) }
    }
    addConstraint("content_ids must be unique") { request ->
        request.contentIds.isNotEmpty() &&
            request.contentIds.size <= 50 &&
            request.contentIds.distinct().size == request.contentIds.size
    }
    addConstraint("due_at is required for critical priority") { request ->
        request.priority != ReviewPriority.CRITICAL || request.dueAt != null
    }
}

val validateIngestionSource = Validation<IngestionSource> {
    addConstraint("http_poll requires poll_interval_seconds >= 60") { source ->
        when (source.sourceType) {
            SourceType.HTTP_POLL -> (source.pollIntervalSeconds ?: 0) >= 60
            else -> source.pollIntervalSeconds == null
        }
    }
}

fun validateConfig(config: WorkspaceConfig): ValidationResult<WorkspaceConfig> {
    val base = validateWorkspaceConfig(config)
    return when (base) {
        is Valid -> validateWorkspaceConfigCrossField(config)
        is Invalid -> base
    }
}

fun validateReview(request: ReviewRequest): ValidationResult<ReviewRequest> = validateReviewRequest(request)
