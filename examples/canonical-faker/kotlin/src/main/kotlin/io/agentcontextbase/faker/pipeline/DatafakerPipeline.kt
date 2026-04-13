package io.agentcontextbase.faker.pipeline

import io.agentcontextbase.faker.profiles.Profile
import net.datafaker.Faker
import java.util.Random

object DatafakerPipeline {
    fun describeInterop(profile: Profile): Map<String, String> {
        val faker = Faker(Random(profile.seed.toLong()))
        return mapOf(
            "company" to faker.company().name(),
            "email" to faker.internet().emailAddress(),
            "note" to "Datafaker is a Java library. kotlin-faker provides a more idiomatic Kotlin DSL. Use kotlin-faker for new Kotlin projects; use Datafaker when you already share a Java faker dependency.",
        )
    }
}
