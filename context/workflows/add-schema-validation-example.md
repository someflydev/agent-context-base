# Workflow: Add a Schema Validation Example

## When to Use This Workflow

Use this workflow when a task adds a new canonical schema-validation example in
one language and one lane. This workflow is for teaching, comparison, and
parity work inside `examples/canonical-schema-validation/`, not for wiring
production validation middleware into an application service.

## Prerequisites

- Relevant stack file exists: `context/stacks/schema-validation-{language}.yaml`
- Domain model is defined: `examples/canonical-schema-validation/domain/models.md`
- Fixture corpus exists: `examples/canonical-schema-validation/domain/fixtures/`
- `CATALOG.md` exists: `examples/canonical-schema-validation/CATALOG.md`

## Steps

1. Identify the language, library, and lane (`A` / `B` / `C`).
   Use `context/skills/schema-validation-lane-selection.md`.

2. Confirm the target directory does not already contain the example.
   Check `examples/canonical-schema-validation/{language}/{library}/`.

3. Create the example directory and implementation files.
   - use the shared `WorkspaceSyncContext` domain from `domain/models.md`
   - implement all five models: `WorkspaceConfig`, `SyncRun`,
     `WebhookPayload`, `IngestionSource`, and `ReviewRequest`
   - cover nested objects, enums, cross-field rules, optional versus nullable,
     collections, and coercion where the library supports them
   - for Lane B, add a schema export function that outputs JSON Schema
   - for Lane C, show that the type definition, validator, and schema all come
     from the same source construct

4. Load the shared fixture corpus.
   Use:
   - `examples/canonical-schema-validation/domain/fixtures/valid/`
   - `examples/canonical-schema-validation/domain/fixtures/invalid/`
   - `examples/canonical-schema-validation/domain/fixtures/edge/`
   Every example must accept valid fixtures, reject invalid fixtures, and test
   edge fixtures explicitly.

5. Write a smoke test in `verification/schema-validation/{language}/`.
   Use `unittest` only, not `pytest`. The smoke test must run the example
   against valid, invalid, and edge fixtures.

6. Update `examples/canonical-schema-validation/CATALOG.md`.
   Register the language, library, lane, status, and file path.

7. Update `examples/canonical-schema-validation/PARITY.md` if needed.
   Record any cross-language divergence that changes parity assumptions or
   fixture interpretation.

8. Run the verification gates before committing.
   - `python3 -m unittest discover -s verification/schema-validation -p "test_*.py" -v`
   - `python3 scripts/validate_context.py`

## Lane-Specific Notes

### Lane A: runtime validation

Focus on what happens to live values. Document the error type, whether the
library fails fast or accumulates errors, and how coercion behaves when the
input is close to valid but not exact.

### Lane B: contract generation

Export the JSON Schema document and assert that it is valid JSON. Assert that
required fields and representation details match the shared domain spec. Run a
round-trip drift check using the contract-generation skill guidance.

### Lane C: hybrid type-driven

Demonstrate that the model type, validation behavior, and schema export all
derive from the same definition construct. Show one change to the definition
and verify that all three surfaces move together.

## Verification Notes

- valid-only tests are insufficient; every example needs rejection coverage
- edge fixtures matter for nullable, optional, enum, and coercion behavior
- if the example exports a contract for downstream consumers, drift checks are
  part of completion, not an optional add-on
- keep one language and one library per example directory to avoid mixed signals

## Common Pitfalls

- confusing contract generation with runtime validation
- adding a language-specific domain instead of reusing `WorkspaceSyncContext`
- writing `pytest`-only verification when the repo expects `unittest`
- skipping catalog updates after adding the implementation
- omitting parity notes when a language behaves differently on coercion or nullability

## Commit Format

`[PROMPT_XXX] add {language}/{library} schema-validation example (Lane {A/B/C})`
