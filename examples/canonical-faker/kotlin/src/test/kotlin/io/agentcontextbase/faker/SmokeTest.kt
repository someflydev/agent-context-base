package io.agentcontextbase.faker

import io.agentcontextbase.faker.pipeline.KotlinFakerPipeline
import io.agentcontextbase.faker.profiles.Profile
import io.agentcontextbase.faker.validate.validate
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

class SmokeTest {
    @Test
    fun smokeProducesCorrectOrgCount() {
        val dataset = KotlinFakerPipeline.generate(Profile.SMOKE)
        assertEquals(3, dataset.organizations.size)
    }

    @Test
    fun smokePassesValidation() {
        val dataset = KotlinFakerPipeline.generate(Profile.SMOKE)
        val report = validate(dataset)
        assertTrue(report.ok, "Violations: ${report.violations}")
    }

    @Test
    fun smokeIsReproducible() {
        val left = KotlinFakerPipeline.generate(Profile.SMOKE)
        val right = KotlinFakerPipeline.generate(Profile.SMOKE)
        assertEquals(left.organizations, right.organizations)
    }
}
