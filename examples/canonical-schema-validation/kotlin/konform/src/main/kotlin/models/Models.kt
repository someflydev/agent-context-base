package models

/**
 * Kotlin data class — no annotations.
 * Validation rules are defined externally in Validators.kt using Konform DSL.
 */
enum class PlanType {
    FREE,
    PRO,
    ENTERPRISE,
}

/**
 * Kotlin data class — no annotations.
 * Validation rules are defined externally in Validators.kt using Konform DSL.
 */
enum class SyncStatus {
    PENDING,
    RUNNING,
    SUCCEEDED,
    FAILED,
    CANCELLED,
}

/**
 * Kotlin data class — no annotations.
 * Validation rules are defined externally in Validators.kt using Konform DSL.
 */
enum class TriggerType {
    MANUAL,
    SCHEDULED,
    WEBHOOK,
}

/**
 * Kotlin data class — no annotations.
 * Validation rules are defined externally in Validators.kt using Konform DSL.
 */
enum class WebhookEventType {
    SYNC_COMPLETED,
    SYNC_FAILED,
    WORKSPACE_SUSPENDED,
}

/**
 * Kotlin data class — no annotations.
 * Validation rules are defined externally in Validators.kt using Konform DSL.
 */
enum class SourceType {
    HTTP_POLL,
    WEBHOOK_PUSH,
    FILE_WATCH,
    DATABASE_CDC,
}

/**
 * Kotlin data class — no annotations.
 * Validation rules are defined externally in Validators.kt using Konform DSL.
 */
enum class ReviewPriority {
    LOW,
    NORMAL,
    HIGH,
    CRITICAL,
}

/**
 * Kotlin data class — no annotations.
 * Validation rules are defined externally in Validators.kt using Konform DSL.
 */
data class SettingsBlock(
    val retryMax: Int,
    val timeoutSeconds: Int,
    val notifyOnFailure: Boolean,
    val webhookUrl: String? = null,
)

/**
 * Kotlin data class — no annotations.
 * Validation rules are defined externally in Validators.kt using Konform DSL.
 */
data class WorkspaceConfig(
    val id: String,
    val name: String,
    val slug: String,
    val ownerEmail: String,
    val plan: PlanType,
    val maxSyncRuns: Int,
    val settings: SettingsBlock,
    val tags: List<String> = emptyList(),
    val createdAt: String,
    val suspendedUntil: String? = null,
)

/**
 * Kotlin data class — no annotations.
 * Validation rules are defined externally in Validators.kt using Konform DSL.
 */
data class SyncRun(
    val runId: String,
    val workspaceId: String,
    val status: SyncStatus,
    val trigger: TriggerType,
    val startedAt: String? = null,
    val finishedAt: String? = null,
    val durationMs: Long? = null,
    val recordsIngested: Long? = null,
    val errorCode: String? = null,
)

/**
 * Kotlin data class — no annotations.
 * Validation rules are defined externally in Validators.kt using Konform DSL.
 */
sealed class WebhookData

/**
 * Kotlin data class — no annotations.
 * Validation rules are defined externally in Validators.kt using Konform DSL.
 */
data class SyncCompletedData(
    val runId: String,
    val workspaceId: String,
    val durationMs: Long,
    val recordsIngested: Long,
) : WebhookData()

/**
 * Kotlin data class — no annotations.
 * Validation rules are defined externally in Validators.kt using Konform DSL.
 */
data class SyncFailedData(
    val runId: String,
    val workspaceId: String,
    val errorCode: String,
    val errorMessage: String,
) : WebhookData()

/**
 * Kotlin data class — no annotations.
 * Validation rules are defined externally in Validators.kt using Konform DSL.
 */
data class WorkspaceSuspendedData(
    val workspaceId: String,
    val suspendedUntil: String,
    val reason: String,
) : WebhookData()

/**
 * Kotlin data class — no annotations.
 * Validation rules are defined externally in Validators.kt using Konform DSL.
 */
data class WebhookPayload(
    val eventType: WebhookEventType,
    val payloadVersion: String,
    val timestamp: String,
    val signature: String,
    val data: WebhookData,
)

/**
 * Kotlin data class — no annotations.
 * Validation rules are defined externally in Validators.kt using Konform DSL.
 */
sealed class SourceConfig

/**
 * Kotlin data class — no annotations.
 * Validation rules are defined externally in Validators.kt using Konform DSL.
 */
data class HttpPollConfig(
    val url: String,
    val method: String,
    val headers: Map<String, String> = emptyMap(),
) : SourceConfig()

/**
 * Kotlin data class — no annotations.
 * Validation rules are defined externally in Validators.kt using Konform DSL.
 */
data class WebhookPushConfig(
    val path: String,
    val secret: String,
) : SourceConfig()

/**
 * Kotlin data class — no annotations.
 * Validation rules are defined externally in Validators.kt using Konform DSL.
 */
data class FileWatchConfig(
    val path: String,
    val pattern: String,
) : SourceConfig()

/**
 * Kotlin data class — no annotations.
 * Validation rules are defined externally in Validators.kt using Konform DSL.
 */
data class DatabaseCdcConfig(
    val dsn: String,
    val table: String,
    val cursorField: String,
) : SourceConfig()

/**
 * Kotlin data class — no annotations.
 * Validation rules are defined externally in Validators.kt using Konform DSL.
 */
data class IngestionSource(
    val sourceId: String,
    val sourceType: SourceType,
    val config: SourceConfig,
    val enabled: Boolean,
    val pollIntervalSeconds: Int? = null,
)

/**
 * Kotlin data class — no annotations.
 * Validation rules are defined externally in Validators.kt using Konform DSL.
 */
data class ReviewRequest(
    val requestId: String,
    val workspaceId: String,
    val reviewerEmails: List<String>,
    val contentIds: List<String>,
    val priority: ReviewPriority,
    val dueAt: String? = null,
    val notes: String? = null,
)
