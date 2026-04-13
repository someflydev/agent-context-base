package io.agentcontextbase.faker;

import io.agentcontextbase.faker.domain.TenantCoreEntities;
import io.agentcontextbase.faker.pipeline.TenantCorePipeline;
import io.agentcontextbase.faker.profiles.Profile;
import io.agentcontextbase.faker.validate.ValidationReport;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

class SmokeTest {
    @Test
    void smokeProducesCorrectOrgCount() {
        TenantCoreEntities.TenantCoreDataset dataset = TenantCorePipeline.generate(Profile.SMOKE);
        assertEquals(3, dataset.organizations().size());
    }

    @Test
    void smokePassesValidation() {
        TenantCoreEntities.TenantCoreDataset dataset = TenantCorePipeline.generate(Profile.SMOKE);
        ValidationReport report = TenantCorePipeline.validate(dataset);
        assertTrue(report.ok(), "Violations: " + report.violations());
    }

    @Test
    void smokeIsReproducible() {
        TenantCoreEntities.TenantCoreDataset left = TenantCorePipeline.generate(Profile.SMOKE);
        TenantCoreEntities.TenantCoreDataset right = TenantCorePipeline.generate(Profile.SMOKE);
        assertEquals(left.organizations(), right.organizations());
    }
}
