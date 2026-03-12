# Add Smoke Tests

Purpose: create fast operational confidence checks.

Sequence:

1. identify the one or two most important happy paths
2. decide whether the smoke is local-only or Docker-backed
3. target the isolated test stack when infra is involved
4. verify setup, execution, and failure messaging

Pitfalls:

- testing too much
- using dev data or ports
