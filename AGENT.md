# AGENT.md

Purpose: boot an assistant into the smallest useful context bundle for this repo.

Read [`docs/context-boot-sequence.md`](docs/context-boot-sequence.md) first. This repo now has a canonical spec/validation layer for `.acb/` generation, plus a repo-local runtime-state workflow for session restart and checkpointing.

## First Reads

1. [`README.md`](README.md)
2. [`docs/context-boot-sequence.md`](docs/context-boot-sequence.md)
3. [`docs/runtime-state-workflow.md`](docs/runtime-state-workflow.md)
4. run `python3 scripts/work.py resume`
   Read the Session Context Briefing it prints before loading more files.
   If it shows a relevant `memory/summaries/` file, load that first.
   If the complexity budget is heavy, prune before broad startup reading.
5. Check `memory/INDEX.md` for orientation; if a relevant `memory/summaries/PROMPT_XX_resume.md`
   exists for the work being resumed, read it.
6. [`docs/usage/SPEC_DRIVEN_ACB_PAYLOADS.md`](docs/usage/SPEC_DRIVEN_ACB_PAYLOADS.md)
7. [`docs/usage/ASSISTANT_BEHAVIOR_SPEC.md`](docs/usage/ASSISTANT_BEHAVIOR_SPEC.md)
8. [`docs/repo-layout.md`](docs/repo-layout.md)
9. one router, one workflow, one stack, and one example only if the task still needs narrowing

## Operating Rules

- Treat `.acb/` as the generated repo-local operating boundary.
- Treat `tmp/*.md`, `context/TASK.md`, `context/SESSION.md`, and
  `context/MEMORY.md` as local runtime state, not doctrine.
- After `work.py resume`, use its git anchor, recent-change clues, next-step
  signal, and plan-review signal to decide what to read next. Then read
  `context/TASK.md` and `context/SESSION.md`; read `context/MEMORY.md` only
  when durable repo-local truths matter; read `tmp/*.md` only when there is an
  active local markdown checkbox checklist or action plan for the current
  session; read `PLAN.md` only when milestone context matters.
- After reading `context/TASK.md` and `context/SESSION.md`, refresh them when
  they are stale relative to the current prompt boundary, recent commits, or
  active changed-file surface. Do not assume `work.py checkpoint` rewrites
  stale runtime notes automatically; update the files when the active slice or
  next safe step has changed.
- Read `memory/INDEX.md` after `work.py resume` when resuming interrupted work or starting a new prompt. Consult `memory/summaries/` for the relevant prompt's context.
- When working in a generated repo, re-read `.acb/SESSION_BOOT.md`, `.acb/profile/selection.json`, `.acb/specs/AGENT_RULES.md`, and `.acb/specs/VALIDATION.md` at session start.
- Prefer manifest-defined bundles over improvised loading.
- When starting a medium or larger session, optionally write a startup trace with `work.py startup-trace write` to record declared context loads for later audit.
- Validation is mandatory before claiming completion unless the operator explicitly waives it.
- Use `blocked`, `incomplete`, and `done` precisely.
- For Tim Pope style multi-line commit messages, always use a heredoc with
  `EOF` so the commit body contains real line breaks, and never include literal
  `\n` sequences.
- When updating an existing `.prompts/PROMPT_{num}.txt` file, use a commit
  subject prefix of `[UPDATE PROMPT_{num}]` instead of the base prompt prefix.
- Do not add `memory/summaries/` or `memory/sessions/` file entries to
  `memory/INDEX.md`; those directories are gitignored and should only be
  described at the tier level, not indexed file-by-file.
- Before committing, group changes into coherent chunks so each commit is a
  single logical unit with a focused Tim Pope style message.
- Use `python3 scripts/work.py checkpoint` at natural boundaries.
- `python3 scripts/work.py checkpoint` is a review point, not a guarantee that
  `context/TASK.md` or `context/SESSION.md` will be rewritten for you.
- Use `python3 scripts/work.py init-project` to initialize the operator console for a project. Use `work.py next` before starting a fresh session to check queue state and quota readiness.
- For session-scoped planning and execution tracking, use markdown files in
  `tmp/`, and make checklist files actual markdown checklists with `- [ ]` /
  `- [x]` checkboxes so work can be checked off as it is done. For example,
  use `tmp/PROMPT_123_checklist.md` or `tmp/runtime-fix-plan.md`. Keep them
  concise and do not commit them.
- If you create a handoff for the next session, create `tmp/HANDOFF.md`.
  Treat it as local-only runtime state and do not commit it.
- Update `PLAN.md` only when a `.prompts` megaprompt or a major decision materially reshapes phases, milestones, or the near-to-mid-term roadmap.
- Keep `context/MEMORY.md` durable and clean; keep active-step detail in `context/TASK.md` and `context/SESSION.md`.
- If a repo provides `PLAN.example.md`, `context/TASK.example.md`, `context/SESSION.example.md`, or `context/MEMORY.example.md`, `init` and `checkpoint` will use those as scaffold sources for missing runtime files.

## New Repo Routing

- When started in `agent-context-base`, assume the operator wants a new generated repo unless they explicitly say they want to modify the base repo itself.
- For new generated repos, prefer `scripts/new_repo.py` over manual scaffolding.
- Make storage, queue, search, and deployment assumptions explicit before generation.
- Pass the operator prompt through `--initial-prompt-text` or `--initial-prompt-file` whenever possible.

## Dogfooding Repo Artifacts

When implementing a new arc, prefer dogfooding existing repo artifacts over building parallel infrastructure.

- Seed data for new canonical examples should use the canonical-faker domain (`examples/canonical-faker/`) and its generation helpers where they exist.
- New doctrines should reference and build on related existing doctrines rather than repeating or silently contradicting them.
- New skills and workflows should link to existing skills and workflows they depend on.

Dogfooding is not optional: it is the mechanism that keeps the repo's artifacts coherent and its context system trustworthy. A new example that builds parallel seed infrastructure is a signal that the canonical-faker arc's outputs are not usable — which is itself a bug to fix.

## Verification

- Base repo: `python scripts/validate_context.py`
- Generated repo: `python .acb/scripts/acb_verify.py`
- Inspect payload: `python .acb/scripts/acb_inspect.py`
- Context tools (when available): `python3 scripts/work.py budget-report --bundle <files>` - scored bundle evaluation
- Context tools (when available): `python3 scripts/work.py route-check "<prompt>"` - heuristic capability routing

## JWT Auth, RBAC, and Multi-Tenant Patterns

The jwt-auth arc (PROMPT_134–140) adds canonical examples for JWT-backed
authentication and RBAC across 8 backend languages. All examples share the
same domain spec, permission catalog, and fixture data.

Key docs:
- `context/doctrine/jwt-auth-request-context.md`
- `context/doctrine/rbac-permission-taxonomy.md`
- `context/doctrine/route-metadata-registry.md`
- `context/doctrine/me-endpoint-discoverability.md`
- `examples/canonical-auth/` (after PROMPT_136–139)

Quick answers:
- Permission naming: `{service}:{resource}:{action}`
- Preferred libraries: PyJWT (Python), jose (TS), golang-jwt/jwt (Go),
  jsonwebtoken (Rust), JJWT (Java/Kotlin), ruby-jwt (Ruby), Joken (Elixir)
- `/me` endpoint: JSON + optional HTMX variant, filtered by effective permissions
