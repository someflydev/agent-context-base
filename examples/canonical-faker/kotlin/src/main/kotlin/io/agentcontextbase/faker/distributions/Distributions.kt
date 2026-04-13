package io.agentcontextbase.faker.distributions

import kotlin.random.Random

object Distributions {
    fun weightedPlan(random: Random): String = pick(random, listOf("free", "free", "free", "free", "free", "pro", "pro", "pro", "pro", "enterprise"))
    fun weightedRegion(random: Random): String = pick(random, listOf("us-east", "us-east", "us-east", "us-east", "us-west", "us-west", "eu-west", "eu-west", "ap-southeast"))
    fun weightedLocale(random: Random): String = pick(random, listOf("en-US", "en-US", "en-US", "en-US", "en-US", "en-US", "en-GB", "en-GB", "de-DE", "fr-FR"))
    fun weightedMembershipRole(random: Random): String = pick(random, listOf("admin", "member", "member", "member", "member", "member", "member", "viewer", "viewer", "viewer"))
    fun weightedProjectStatus(random: Random): String = pick(random, listOf("active", "active", "active", "active", "active", "active", "archived", "archived", "draft", "draft"))
    fun weightedInvitationRole(random: Random): String = pick(random, listOf("admin", "member", "member", "member", "viewer", "viewer"))
    fun weightedAuditAction(random: Random): String = pick(random, listOf("created", "created", "updated", "updated", "updated", "deleted", "archived", "invited", "exported"))
    fun weightedResourceType(random: Random): String = pick(random, listOf("project", "project", "project", "user", "membership", "membership", "api_key", "invitation"))

    fun memberCount(random: Random, userCount: Int): Int {
        val max = minOf(userCount, 8).coerceAtLeast(3)
        return random.nextInt(from = 3, until = max + 1)
    }

    fun projectCount(random: Random): Int = random.nextInt(from = 2, until = 5)
    fun apiKeyCount(random: Random): Int = random.nextInt(from = 1, until = 3)
    fun invitationCount(random: Random): Int = random.nextInt(from = 1, until = 3)

    fun auditEventCount(random: Random, status: String): Int = when (status) {
        "active" -> random.nextInt(from = 8, until = 15)
        "archived" -> random.nextInt(from = 4, until = 9)
        else -> random.nextInt(from = 3, until = 6)
    }

    private fun pick(random: Random, values: List<String>): String = values[random.nextInt(values.size)]
}
