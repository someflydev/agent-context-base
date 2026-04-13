package io.agentcontextbase.faker

import com.fasterxml.jackson.module.kotlin.jacksonObjectMapper
import io.agentcontextbase.faker.pipeline.KotlinFakerPipeline
import io.agentcontextbase.faker.pools.IdPools
import io.agentcontextbase.faker.profiles.Profile
import io.agentcontextbase.faker.validate.validate
import java.nio.file.Path

fun main(args: Array<String>) {
    var profileName = "smoke"
    var outputDir = "./output"
    var seedOverride: Int? = null

    var index = 0
    while (index < args.size) {
        when (args[index]) {
            "--profile" -> profileName = args.getOrNull(++index) ?: "smoke"
            "--output" -> outputDir = args.getOrNull(++index) ?: "./output"
            "--seed" -> seedOverride = args.getOrNull(++index)?.toIntOrNull()
        }
        index += 1
    }

    val profile = Profile.resolve(profileName, seedOverride)
    val dataset = KotlinFakerPipeline.generate(profile)
    val report = validate(dataset)
    println(jacksonObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(report))
    require(report.ok) { "Validation failed: ${report.violations}" }
    IdPools.writeJsonl(Path.of(outputDir).resolve(profile.name), dataset, report)
}
