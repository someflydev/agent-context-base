# Repo Layout

The repository is intentionally layered so assistants can load only what they need.

## Top-Level Files

- `README.md`: top-level overview and loading order
- `AGENT.md`: concise Codex-style router
- `CLAUDE.md`: concise Claude-oriented router
- `.gitignore`: practical ignore rules across the supported stacks

## `docs/`

Repo-level orientation only. Keep these files short and stable.

- `docs/repo-purpose.md`
- `docs/repo-layout.md`

## `context/doctrine/`

Stable rules. Use for decisions that should survive across tasks:

- naming
- testing
- smoke-test scope
- compose naming and data isolation
- commits
- prompt-first conventions
- canonical examples
- context loading
- Dokku deployment philosophy

## `context/workflows/`

Task playbooks. Each workflow should describe:

- when it applies
- preconditions
- sequence
- outputs
- required smoke tests
- when minimal real-infra integration tests are also required

## `context/stacks/`

Concrete implementation guidance for first-class stacks and infra components. Keep these grounded in real file paths, change surfaces, and test implications.

## `context/archetypes/`

Project-shape guidance. Use when the task is about the kind of repo being built, not just one framework.

## `context/router/`

Inference rules and aliases that help assistants map normal language onto the right workflow, archetype, stack, and example bundle.

## `context/skills/`

Short reusable capability docs. These should stay operational and composable instead of repeating doctrine or stack details.

## `manifests/`

Machine-readable context bundles. They describe expected stacks, likely triggers, required context, optional context, preferred examples, and warnings.

## `examples/`

Canonical example surfaces. They document what a strong example of each category should contain. These are not scaffolds.

## `templates/`

Starter scaffolds. These are intentionally lighter than examples and should never override doctrine or canonical example guidance.

## `scripts/`

Small utilities for validating manifests and previewing context bundles. Keep them dependency-light and readable.

## `smoke-tests/`

Repo-level guidance for future projects. This base repo does not pretend to ship one-size-fits-all smoke tests for every descendant repo.

## Extension Rule

When adding new stacks later, extend the same pattern:

1. add a focused stack doc
2. add aliases
3. add manifests if the stack becomes first-class
4. add examples only when there is a stable canonical pattern

