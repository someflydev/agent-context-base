# Multi-Storage Experiment

Use this archetype for repos intentionally comparing or combining multiple storage systems in one project.

## Common Goals

- make each storage boundary explicit
- keep comparison scope narrow
- isolate ports, data roots, and fixtures cleanly

## Required Context

- `context/doctrine/compose-port-and-data-isolation.md`
- relevant storage stack docs

## Common Workflows

- `context/workflows/add-storage-integration.md`
- `context/workflows/add-seed-data.md`
- `context/workflows/post-flight-refinement.md`

## Likely Examples

- `examples/canonical-storage/README.md`

## Typical Anti-Patterns

- adding too many storage systems at once
- shared fixtures that hide boundary differences
- no test isolation between services

