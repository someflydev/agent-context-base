# CLI Tool

Use this archetype for command-line utilities that may read files, call APIs, or manage local workflows.

## Common Goals

- explicit command structure
- predictable output
- good help text
- fast smoke verification

## Required Context

- `context/doctrine/testing-philosophy.md`
- `context/workflows/extend-cli.md`

## Common Workflows

- `context/workflows/extend-cli.md`
- `context/workflows/add-feature.md`
- `context/workflows/fix-bug.md`

## Likely Examples

- `examples/canonical-cli/README.md`

## Typical Anti-Patterns

- hidden side effects
- output formats that are hard to parse
- no smoke path for the primary command

