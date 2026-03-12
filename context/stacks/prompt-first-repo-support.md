# Prompt-First Repo Support

Purpose: capture stack-like conventions for prompt-first repos that are organized around ordered prompts, operator guides, manifests, and assistant routers rather than a single application runtime.

Common file paths:

- `.prompts/`
- `AGENT.md`
- `CLAUDE.md`
- `docs/`
- `manifests/`

Typical change surfaces:

- prompt ordering
- operator guidance
- manifest routing hints
- canonical prompt examples

Testing expectations:

- smoke checks for prompt presence and routing references
- documentation link validation

Common mistake:

- treating prompt-first repos as if they need full backend stack docs for every task
