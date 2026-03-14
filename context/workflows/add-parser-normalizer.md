# Add Parser And Normalizer

## Purpose

Convert raw payloads from one or more sources into stable normalized records.

## When To Use It

- raw payloads are retained and need shaping for storage or APIs
- multiple sources need a shared canonical schema

## Inputs

- raw payload contract
- normalized schema
- provenance requirements

## Sequence

1. define the canonical record shape and required identifiers
2. parse each source payload into an intermediate source-local shape if needed
3. normalize into the shared model with explicit source provenance
4. preserve parse warnings and partial-field confidence where ambiguity matters
5. write idempotent upsert or merge behavior into the persistence stage
6. verify at least one raw-to-normalized example per source

## Outputs

- parser functions
- normalized schema contract
- provenance-aware record mapping

## Related Doctrine

- `context/doctrine/data-acquisition-philosophy.md`
- `context/doctrine/raw-data-retention.md`

## Common Pitfalls

- letting one source's odd schema become the global model
- discarding parse ambiguity instead of surfacing it
- coupling parser output directly to frontend display needs

## Stop Conditions

- normalized records still depend on source-specific field names
- provenance is lost during normalization
- parser logic cannot run against archived raw inputs alone
