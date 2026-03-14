# Data Acquisition Invariants

Use this document as the language-agnostic contract for data acquisition work.

`PROMPT_30` established the doctrine and workflow surface for acquisition-heavy repos. The remaining gap was that the canonical example layer still read as Python-first. This invariant layer makes the cross-language rules explicit so assistants and contributors can separate what must stay true in every stack from what belongs in a stack-specific implementation.

## Layering Rule

- doctrine and workflows define cross-language invariants
- canonical examples define completed stack-specific implementations
- a canonical example must be real code or a real runnable bundle, not pseudocode written in the shape of code
- verification claims must match repository automation exactly

## Stage Boundaries

- separate fetch, archive, parse, normalize, classify, and persist boundaries when that separation improves replay, retry, or recovery
- keep source adapters narrow; selectors, auth quirks, pagination, and transport handling belong near the source boundary
- keep orchestration code focused on scheduling, replay, and state transitions instead of source-specific extraction details

## Raw Preservation

- preserve raw source material before irreversible transforms when feasible
- keep raw bodies and raw metadata adjacent so re-parse does not depend on live upstream access
- do not let normalized outputs overwrite or replace durable raw captures

## Provenance And Re-Parseability

- every normalized record should retain explicit source provenance
- preserve enough metadata to re-parse later without calling the upstream again
- keep source identifiers, fetch time, raw artifact location, and adapter or parser version available to downstream stages
- classification or enrichment outputs should record classifier version, input boundary, and confidence when used

## Canonical Model Discipline

- do not let one source schema leak directly into the shared canonical model
- normalize after the fetch boundary, not inside transport code
- treat per-source oddities as adapter concerns unless the canonical model truly needs the field

## Operational Boundaries

- treat sync triggers, retries, rate limits, and backoff as operational boundaries rather than UI concerns
- prefer incremental, repeatable pulls with explicit checkpoints over destructive full reloads
- make duplicate or replayed sync requests converge safely instead of amplifying writes

## Canonical Example Contract

- a canonical data acquisition example must be a completed implementation in the target language or stack
- prose and invariant docs can explain the pattern, but they do not count as a stack-specific canonical implementation
- if no stack-matching acquisition example exists yet, say so explicitly
- when no stack-matching acquisition example exists, fall back to these invariants plus the closest honestly verified example in the target stack

## Selection Rule

- start with this file when the user asks for generic acquisition guidance or has not picked a stack yet
- once the stack is known, prefer the closest stack-matching acquisition example with the highest honest verification level
- if the closest available example is outside the acquisition capability area, label it as a fallback rather than a canonical acquisition example
