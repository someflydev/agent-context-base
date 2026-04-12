import com.google.gson.Gson
import com.google.gson.JsonObject
import com.google.gson.JsonParser
import models.PlanType
import models.ReviewPriority
import models.ReviewRequest
import models.SettingsBlock
import models.WorkspaceConfig
import validation.validateConfig
import validation.validateReview
import java.nio.file.Paths

private val gson = Gson()

private fun fixturesRoot() =
    Paths.get("..", "..", "domain", "fixtures")

private fun loadJson(path: String): JsonObject {
    val text = fixturesRoot().resolve(path).toFile().readText()
    return JsonParser.parseString(text).asJsonObject
}

private fun workspaceConfigFromFixture(path: String): WorkspaceConfig {
    val json = loadJson(path)
    val settings = json.getAsJsonObject("settings")
    return WorkspaceConfig(
        id = json.get("id").asString,
        name = json.get("name").asString,
        slug = json.get("slug").asString,
        ownerEmail = json.get("owner_email").asString,
        plan = PlanType.valueOf(json.get("plan").asString.uppercase()),
        maxSyncRuns = json.get("max_sync_runs").asInt,
        settings = SettingsBlock(
            retryMax = settings.get("retry_max").asInt,
            timeoutSeconds = settings.get("timeout_seconds").asInt,
            notifyOnFailure = settings.get("notify_on_failure").asBoolean,
            webhookUrl = settings.get("webhook_url").takeIf { !it.isJsonNull }?.asString,
        ),
        tags = json.getAsJsonArray("tags").map { it.asString },
        createdAt = json.get("created_at").asString,
        suspendedUntil = json.get("suspended_until").takeIf { !it.isJsonNull }?.asString,
    )
}

private fun reviewRequestFromFixture(path: String): ReviewRequest {
    val json = loadJson(path)
    return ReviewRequest(
        requestId = json.get("request_id").asString,
        workspaceId = json.get("workspace_id").asString,
        reviewerEmails = json.getAsJsonArray("reviewer_emails").map { it.asString },
        contentIds = json.getAsJsonArray("content_ids").map { it.asString },
        priority = ReviewPriority.valueOf(json.get("priority").asString.uppercase()),
        dueAt = json.get("due_at").takeIf { !it.isJsonNull }?.asString,
        notes = json.get("notes").takeIf { !it.isJsonNull }?.asString,
    )
}

private fun printWorkspaceValidation(path: String) {
    val result = validateConfig(workspaceConfigFromFixture(path))
    when (result) {
        is io.konform.validation.Valid -> println("$path PASS")
        is io.konform.validation.Invalid -> println("$path FAIL: ${result.errors}")
    }
}

private fun printReviewValidation(path: String) {
    val result = validateReview(reviewRequestFromFixture(path))
    when (result) {
        is io.konform.validation.Valid -> println("$path PASS")
        is io.konform.validation.Invalid -> println("$path FAIL: ${result.errors}")
    }
}

fun main() {
    printWorkspaceValidation("valid/workspace_config_basic.json")
    printWorkspaceValidation("invalid/workspace_config_plan_too_many_runs.json")
    printReviewValidation("invalid/review_request_critical_no_due_date.json")
}
