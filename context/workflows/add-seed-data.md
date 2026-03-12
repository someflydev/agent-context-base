# Add Seed Data

Purpose: create deterministic data initialization flows.

Sequence:

1. separate dev seeds from test fixtures
2. keep seed scripts idempotent where possible
3. document target stores and data paths
4. verify test seeds only touch isolated test resources

Pitfalls:

- one script seeding both dev and test
- hidden assumptions about persistent volumes
