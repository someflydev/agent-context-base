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

Doctrine and workflows describe cross-language rules. Canonical examples describe completed stack-specific implementations.

## Selection Rules

- prefer one canonical example per pattern family
- prefer examples that match the active stack and archetype
- prefer the highest honestly verified example when several stack-matching options exist
- use `examples/catalog.json` when ranking several plausible examples
- use `verification/example_registry.yaml` when trust level or verification depth matters
- retire examples that contradict doctrine or newer first-class stack guidance

## Examples Versus Templates

- examples show a preferred completed pattern
- examples must be real code or real runnable assets when they claim a stack-specific implementation
- templates provide a starting scaffold

Do not treat templates as proof that a pattern is production-worthy.
Do not treat pseudocode, mixed-language snippets, or aspirational prose as canonical implementations.

## Example Drift Prevention

When doctrine changes, review affected examples quickly. A stale example is often worse than no example.

## When No Example Exists

If no canonical example fits, say so explicitly and implement the smallest doctrine-consistent solution. Fall back to the relevant invariant docs plus the closest honestly verified example. Consider adding a new canonical example only if the pattern is likely to recur.
