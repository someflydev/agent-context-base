# Post-Flight Refinement Checklist

Use this after the main implementation works.

1. Confirm every file reference still exists after the final rename or move.
2. Confirm the active manifest still points at the best canonical example and template set.
3. Remove comments that only repeat obvious code behavior.
4. Tighten smoke tests to one clear happy path with readable failure output.
5. Add or update one real-infra integration test if the change crosses storage or service boundaries.
6. Confirm `docker-compose.yml` and `docker-compose.test.yml` still use distinct host ports and data roots.
7. Rerun manifest validation and the smallest relevant test suite.
8. Split the work into reviewable commits if the change mixed schema, examples, and scripts.

