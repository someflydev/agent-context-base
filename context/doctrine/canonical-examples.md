# Canonical Examples

Examples should reduce ambiguity, not create it.

## Purpose

Use canonical examples to show the preferred pattern for a recurring problem:

- API route shape
- smoke-test structure
- Dokku deployment wiring
- prompt-file organization
- seed data flow
- storage integration
- local RAG indexing

## Selection Rules

- prefer one canonical example per pattern family
- prefer examples that match the active stack and archetype
- use `examples/catalog.json` when ranking several plausible examples
- retire examples that contradict doctrine or newer first-class stack guidance

## Examples Versus Templates

- examples show a preferred completed pattern
- templates provide a starting scaffold

Do not treat templates as proof that a pattern is production-worthy.

## Example Drift Prevention

When doctrine changes, review affected examples quickly. A stale example is often worse than no example.

## When No Example Exists

If no canonical example fits, say so explicitly and implement the smallest doctrine-consistent solution. Consider adding a new canonical example only if the pattern is likely to recur.
