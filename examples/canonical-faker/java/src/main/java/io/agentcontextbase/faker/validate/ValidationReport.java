package io.agentcontextbase.faker.validate;

import java.util.List;
import java.util.Map;

public record ValidationReport(
        boolean ok,
        List<String> violations,
        Map<String, Integer> counts,
        long seed,
        String profileName
) {
}
