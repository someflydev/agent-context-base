# Dokku-Deployable Service

Use this archetype for a single-service repo expected to ship on Dokku.

## Common Goals

- explicit boot contract
- simple service boundary
- documented environment variables
- deploy verification through smoke tests

## Required Context

- `context/doctrine/deployment-philosophy-dokku.md`
- `context/stacks/dokku-conventions.md`
- the active service stack doc

## Common Workflows

- `context/workflows/add-deployment-support.md`
- `context/workflows/add-smoke-tests.md`
- `context/workflows/add-storage-integration.md`

## Likely Examples

- `examples/canonical-dokku/README.md`
- `examples/canonical-smoke-tests/README.md`

## Typical Anti-Patterns

- one repo designed as a platform cluster
- undocumented release or migration steps
- trusting deployment without local real-infra verification

