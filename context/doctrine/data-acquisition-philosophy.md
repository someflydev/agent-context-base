# Data Acquisition Philosophy

Use these rules when a repo acquires public or partner data as a first-class capability.

Use `context/doctrine/data-acquisition-invariants.md` for the explicit language-agnostic contract. Use stack-specific canonical examples only when they are real completed implementations in the target language.

## Preserve Re-Parseability

- keep fetched payloads or documents before irreversible transforms when practical
- prefer immutable raw captures plus derived parsed tables over one-way mutation
- record source identifiers, fetch time, and adapter version with every durable write

## Separate Stages Cleanly

- fetching, raw archival, parsing, normalization, classification, and serving are different concerns
- keep source adapters narrow; do not hide parsing or classification inside transport code
- frontend needs must not dictate how acquisition stages are coupled internally

## Prefer Incremental Repeatable Pulls

- favor explicit windows, cursors, checkpoints, or high-water marks over full reloads
- make repeat runs safe; a duplicate sync should converge instead of amplify damage
- optimize for replay from archived raw data before inventing destructive cleanup

## Track Provenance Explicitly

- every normalized record should point back to source name and raw artifact path when feasible
- enrichment or classification outputs should carry classifier version, inputs, and confidence
- preserve enough lineage to explain why a record exists and how it was shaped

## Bound The Adapter

- keep per-source auth, pagination, selectors, and quirks local to the adapter
- normalize into shared shapes only after the fetch boundary
- do not leak one source's naming or odd fields into the common model casually

## Operational Rule

If a new capability makes re-fetch, re-parse, or replay harder than before, stop and simplify the stage boundaries first.
