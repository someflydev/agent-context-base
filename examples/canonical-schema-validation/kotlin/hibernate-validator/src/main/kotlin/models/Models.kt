package models

import jakarta.validation.Constraint
import jakarta.validation.ConstraintValidator
import jakarta.validation.ConstraintValidatorContext
import jakarta.validation.Payload
import jakarta.validation.Valid
import jakarta.validation.constraints.Email
import jakarta.validation.constraints.Max
import jakarta.validation.constraints.Min
import jakarta.validation.constraints.NotBlank
import jakarta.validation.constraints.NotNull
import jakarta.validation.constraints.Pattern
import jakarta.validation.constraints.Size
import kotlin.reflect.KClass

/**
 * Annotation-driven validation using Jakarta Bean Validation.
 * The annotations live on the data class fields. Validation is performed by a
 * Validator instance (from the Jakarta Validation factory). This is the JVM
 * ecosystem standard — integrates with Spring Boot @Validated, Quarkus, Jakarta EE.
 */
enum class PlanType {
    FREE,
    PRO,
    ENTERPRISE,
}

/**
 * Annotation-driven validation using Jakarta Bean Validation.
 * The annotations live on the data class fields. Validation is performed by a
 * Validator instance (from the Jakarta Validation factory). This is the JVM
 * ecosystem standard — integrates with Spring Boot @Validated, Quarkus, Jakarta EE.
 */
enum class SyncStatus {
    PENDING,
    RUNNING,
    SUCCEEDED,
    FAILED,
    CANCELLED,
}

/**
 * Annotation-driven validation using Jakarta Bean Validation.
 * The annotations live on the data class fields. Validation is performed by a
 * Validator instance (from the Jakarta Validation factory). This is the JVM
 * ecosystem standard — integrates with Spring Boot @Validated, Quarkus, Jakarta EE.
 */
enum class TriggerType {
    MANUAL,
    SCHEDULED,
    WEBHOOK,
}

/**
 * Annotation-driven validation using Jakarta Bean Validation.
 * The annotations live on the data class fields. Validation is performed by a
 * Validator instance (from the Jakarta Validation factory). This is the JVM
 * ecosystem standard — integrates with Spring Boot @Validated, Quarkus, Jakarta EE.
 */
data class SettingsBlock(
    @field:Min(0) @field:Max(10) val retryMax: Int,
    @field:Min(10) @field:Max(3600) val timeoutSeconds: Int,
    val notifyOnFailure: Boolean,
    val webhookUrl: String? = null,
)

@Target(AnnotationTarget.CLASS)
@Retention(AnnotationRetention.RUNTIME)
@Constraint(validatedBy = [WorkspaceConfigValidator::class])
annotation class ValidWorkspaceConfig(
    val message: String = "maxSyncRuns exceeds the limit for the selected plan",
    val groups: Array<KClass<*>> = [],
    val payload: Array<KClass<out Payload>> = [],
)

class WorkspaceConfigValidator : ConstraintValidator<ValidWorkspaceConfig, WorkspaceConfig> {
    override fun isValid(value: WorkspaceConfig?, context: ConstraintValidatorContext): Boolean {
        if (value == null) {
            return true
        }
        val limit = when (value.plan) {
            PlanType.FREE -> 10
            PlanType.PRO -> 100
            PlanType.ENTERPRISE -> 1000
        }
        if (value.maxSyncRuns <= limit) {
            return true
        }
        context.disableDefaultConstraintViolation()
        context.buildConstraintViolationWithTemplate("must be <= $limit for ${value.plan.name.lowercase()} plan")
            .addPropertyNode("maxSyncRuns")
            .addConstraintViolation()
        return false
    }
}

@ValidWorkspaceConfig
data class WorkspaceConfig(
    @field:NotBlank @field:Size(min = 3, max = 100) val name: String,
    @field:NotBlank
    @field:Pattern(regexp = "^[a-z][a-z0-9-]{1,48}[a-z0-9]$")
    val slug: String,
    @field:Email val ownerEmail: String,
    @field:NotNull val plan: PlanType,
    @field:Min(1) @field:Max(1000) val maxSyncRuns: Int,
    @field:Valid @field:NotNull val settings: SettingsBlock,
    @field:Size(max = 20) val tags: List<String> = emptyList(),
    val id: String,
    val createdAt: String,
    val suspendedUntil: String? = null,
)

data class SyncRun(
    val runId: String,
    val workspaceId: String,
    @field:NotNull val status: SyncStatus,
    @field:NotNull val trigger: TriggerType,
    val startedAt: String? = null,
    val finishedAt: String? = null,
    @field:Min(0) val durationMs: Long? = null,
    @field:Min(0) @field:Max(10_000_000) val recordsIngested: Long? = null,
    val errorCode: String? = null,
)
