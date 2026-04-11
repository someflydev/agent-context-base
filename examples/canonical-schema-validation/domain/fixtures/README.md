# WorkspaceSyncContext Fixture Corpus

This directory contains the canonical JSON fixture corpus for the
WorkspaceSyncContext domain. Every language example in the schema-validation
arc must consume these same files.

Layout:

- `valid/` — fixtures that every implementation must accept
- `invalid/` — fixtures that every Lane A implementation must reject
- `edge/` — fixtures with intentionally documented divergence potential

The corpus currently contains 23 fixtures:

- 11 valid
- 8 invalid
- 4 edge

These files are the cross-language contract. Keep filenames stable and do not
edit payload structure casually, because future parity checks and smoke tests
depend on exact consistency.
