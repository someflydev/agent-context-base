# agent-context-base

Reusable base repository for agent-oriented context architecture.

This repo is a starter foundation for future projects that need:

- small, deterministic context loading
- doctrine separated from workflows, stacks, archetypes, and examples
- prompt-first repo support
- Docker-backed dev and test isolation
- canonical-example-first implementation patterns
- consistent routing across Codex, Claude, and Gemini

Start here:

1. Read `AGENT.md` or `CLAUDE.md` depending on the assistant.
2. Read `manifests/repo.profile.yaml`.
3. Follow `context/router/load-order.md`.
4. Load only the smallest relevant doctrine, workflow, archetype, stack, and example bundle for the task.

Primary architecture spec:

- `docs/agent-context-architecture.md`

Repository intent:

- This is not an application repo.
- This is a bootstrap-ready base repo that future projects can copy and adapt.
- The system is designed around durable doctrine, deterministic routing, and canonical examples rather than giant assistant-specific instruction files.
