import com.google.gson.JsonParser
import jakarta.validation.ConstraintViolation
import jakarta.validation.Validation
import models.PlanType
import models.SettingsBlock
import models.WorkspaceConfig
import java.nio.file.Paths

private fun fixturesRoot() =
    Paths.get("..", "..", "domain", "fixtures")

private fun loadConfig(path: String): WorkspaceConfig {
    val json = JsonParser.parseString(fixturesRoot().resolve(path).toFile().readText()).asJsonObject
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

private fun printValidation(path: String) {
    val factory = Validation.buildDefaultValidatorFactory()
    val validator = factory.validator
    val config = loadConfig(path)
    val violations: Set<ConstraintViolation<WorkspaceConfig>> = validator.validate(config)
    if (violations.isEmpty()) {
        println("$path PASS")
    } else {
        violations.forEach { println("$path FAIL: ${it.propertyPath} ${it.message}") }
    }
}

fun main() {
    printValidation("valid/workspace_config_basic.json")
    printValidation("invalid/workspace_config_plan_too_many_runs.json")
}
