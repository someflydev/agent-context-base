# Add Raw Download Archive

## Purpose

Create a durable raw payload archive that supports re-parse and failure triage.

## When To Use It

- a source adapter already exists without retained raw artifacts
- parsing needs to be replayable without re-fetching upstream data

## Inputs

- source names
- expected payload types and sizes
- local retention root
- metadata required for provenance

## Sequence

1. choose a deterministic layout by source and fetch time or sync run
2. define sidecar metadata: checksum, content type, request fingerprint, status, source identifiers
3. separate dev and test archive roots
4. write a small lookup path from normalized record back to raw artifact
5. add one re-parse example or test from archived data

## Outputs

- raw archive layout
- metadata contract
- replay path for parsers

## Related Doctrine

- `context/doctrine/raw-data-retention.md`
- `context/doctrine/data-acquisition-philosophy.md`

## Common Pitfalls

- storing only parsed JSON and calling it raw retention
- using non-deterministic filenames that block replay or debugging
- writing test archives into dev roots

## Stop Conditions

- operators cannot locate a raw payload from a normalized record
- archive metadata is missing checksum, source, or fetch time
- re-parse still requires live upstream access
