# agent-context-base

Reusable base repository for agent-oriented software projects.

This repo is a foundation, not a finished app. It exists to give future repos a strong starting point for:

- prompt-first workflows
- small deterministic context loading
- doctrine separated from workflows, stacks, archetypes, examples, and templates
- canonical-example-first implementation
- Docker-backed local development with strict dev/test isolation
- Dokku-friendly deployment conventions
- consistent routing across Codex, Claude, and Gemini

## Start Here

1. Read `AGENT.md` or `CLAUDE.md`.
2. Read `manifests/repo.profile.yaml`.
3. Read `context/router/task-router.md`.
4. Load the smallest relevant doctrine, workflow, archetype, stack, and example bundle.

## Core Spec

- `docs/agent-context-architecture.md`
- `context/router/task-router.md`
- `context/router/stack-router.md`
- `context/router/archetype-router.md`
- `context/router/alias-catalog.md`
- `manifests/README.md`

## What This Repo Is

- A reusable base repo for bootstrapping future projects.
- A context architecture for assistant-guided development.
- A place to keep doctrine, routing rules, manifests, templates, and canonical examples separate.

## What This Repo Is Not

- Not a forever-monorepo for actual products.
- Not a dumping ground for every stack detail in one top-level file.
- Not a substitute for project-specific manifests and examples in future derived repos.
