# Data Acquisition Service

Use this archetype for repos whose primary job is to acquire external data, preserve raw material, normalize it, enrich it, and persist it behind stable operator or API surfaces.

## Common Goals

- narrow source adapters
- replayable raw archive
- explicit parse and classification stages
- stable sync status and operator controls
- clean separation between acquisition and presentation

## Required Context

- `context/doctrine/data-acquisition-invariants.md`
- `context/doctrine/data-acquisition-philosophy.md`
- `context/doctrine/raw-data-retention.md`
- `context/doctrine/sync-safety-rate-limits.md`

## Common Workflows

- `context/workflows/research-data-sources.md`
- `context/workflows/add-api-ingestion-source.md`
- `context/workflows/add-scraping-source.md`
- `context/workflows/add-parser-normalizer.md`
- `context/workflows/add-classification-step.md`

## Likely Examples

- `examples/canonical-data-acquisition/README.md`
- `examples/canonical-data-acquisition/language-support-matrix.yaml`
- `examples/canonical-storage/README.md`

## Typical Anti-Patterns

- no raw retention for operationally important sources
- fetch, parse, classify, and persist collapsed into one job
- frontend-driven shortcuts leaking into source adapters
