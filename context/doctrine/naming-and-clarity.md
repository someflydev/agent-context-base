# Naming And Clarity

Clear naming reduces routing mistakes and implementation drift.

## File Naming Rules

- prefer deterministic filenames over clever names
- use filenames that describe purpose directly
- keep one file focused on one concern
- avoid synonyms for existing concepts when one term already exists in the repo

Examples:

- use `add-api-endpoint.md`, not `endpoint-playbook.md`
- use `typescript-hono-bun.md`, not `bun-service-notes.md`
- use `canonical-examples.md`, not `example-policy-v2.md`

## Writing Rules

- say what the file is for in the first two lines
- prefer direct instructions over abstract commentary
- keep sections short enough to scan during implementation
- make cross-references explicit with exact paths

## Routing Language

Routing docs should mirror how users talk:

- "bug"
- "feature"
- "seed data"
- "local rag"
- "deploy to dokku"

Do not force users to learn internal taxonomy just to get correct routing.

## Naming In Future Repos

When bootstrapping a descendant repo:

- keep service names short and stable
- derive Compose project names from the repo name
- reserve prompt filenames for strictly monotonic numbered sequences
- keep test names descriptive and behavior-focused

