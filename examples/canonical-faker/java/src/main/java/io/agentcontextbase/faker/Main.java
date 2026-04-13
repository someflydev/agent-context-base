package io.agentcontextbase.faker;

import io.agentcontextbase.faker.domain.TenantCoreEntities;
import io.agentcontextbase.faker.pipeline.TenantCorePipeline;
import io.agentcontextbase.faker.pools.IdPools;
import io.agentcontextbase.faker.profiles.Profile;
import io.agentcontextbase.faker.validate.ValidationReport;

import java.nio.file.Path;

public final class Main {
    private Main() {
    }

    public static void main(String[] args) throws Exception {
        String profileName = "smoke";
        String output = "./output";
        Long seedOverride = null;

        for (int index = 0; index < args.length; index++) {
            switch (args[index]) {
                case "--profile" -> profileName = index + 1 < args.length ? args[++index] : "smoke";
                case "--output" -> output = index + 1 < args.length ? args[++index] : "./output";
                case "--seed" -> seedOverride = index + 1 < args.length ? Long.parseLong(args[++index]) : null;
                default -> {
                }
            }
        }

        Profile profile = Profile.resolve(profileName, seedOverride);
        TenantCoreEntities.TenantCoreDataset dataset = TenantCorePipeline.generate(profile);
        ValidationReport report = TenantCorePipeline.validate(dataset);
        System.out.println(new com.fasterxml.jackson.databind.ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(report));
        if (!report.ok()) {
            System.exit(1);
        }
        IdPools.writeJsonl(Path.of(output).resolve(profile.name()), dataset, report);
    }
}
