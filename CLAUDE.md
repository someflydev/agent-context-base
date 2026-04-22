# CLAUDE.md

> **Sync note:** AGENT.md and CLAUDE.md are intentionally near-identical. When
> updating operating rules, update both files. AGENT.md is the source of truth
> for rule wording; CLAUDE.md may add Claude Code-specific notes.

Use this file as a boot entrypoint, not as the full source of truth.

Follow [`docs/context-boot-sequence.md`](docs/context-boot-sequence.md) before broad exploration.

## First Reads

1. [`README.md`](README.md)
2. [`docs/context-boot-sequence.md`](docs/context-boot-sequence.md)
3. [`docs/runtime-state-workflow.md`](docs/runtime-state-workflow.md)
4. run `python3 scripts/work.py resume`
5. `memory/INDEX.md` (if resuming work or starting a new prompt)
6. [`docs/usage/SPEC_DRIVEN_ACB_PAYLOADS.md`](docs/usage/SPEC_DRIVEN_ACB_PAYLOADS.md)
7. [`docs/usage/ASSISTANT_BEHAVIOR_SPEC.md`](docs/usage/ASSISTANT_BEHAVIOR_SPEC.md)
8. [`docs/repo-layout.md`](docs/repo-layout.md)

## Minimal Context Policy

Prefer this order:

1. one router
2. one workflow
3. one active stack surface
4. one archetype if the repo shape matters
5. one canonical example
6. spec/validation modules only when working on `.acb/` composition or hardening

Load one dominant path, not a broad survey.

## Guardrails

- Re-read generated `.acb/` boot files at session start.
- Treat `tmp/*.md`, `context/TASK.md`, `context/SESSION.md`, and
  `context/MEMORY.md` as local runtime state, not doctrine.
- After `work.py resume`, read the Session Context Briefing before loading
  task-specific context. Use it to gauge complexity posture and quota readiness.
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
- After `work.py resume`, check `memory/INDEX.md` and load any `memory/summaries/` artifact relevant to the current work before starting task-specific context loading.
- For medium or larger sessions, use `work.py startup-trace write` to self-declare what was loaded. This feeds into `work.py budget-report` for context scoring.
- Before starting a new prompt session, run `python3 scripts/work.py next` to check the queue, quota state, and whether a resume summary exists.
- Prefer manifests, canonical examples, and validation gates over improvisation.
- Treat templates as scaffolds, not canonical truth.
- Use `python3 scripts/work.py checkpoint` after meaningful changes, before ending a session, and before a likely handoff.
- `python3 scripts/work.py checkpoint` is a review point, not a guarantee that
  `context/TASK.md` or `context/SESSION.md` will be rewritten for you.
- For session-scoped planning and execution tracking, use markdown files in
  `tmp/`, and make checklist files actual markdown checklists with `- [ ]` /
  `- [x]` checkboxes so work can be checked off as it is done. For example,
  use `tmp/PROMPT_123_checklist.md` or `tmp/runtime-fix-plan.md`. Keep them
  concise and do not commit them.
- If you create a handoff for the next session, create `tmp/HANDOFF.md`.
  Treat it as local-only runtime state and do not commit it.
- Update `PLAN.md` only when a `.prompts` megaprompt or a major decision materially reshapes phases, milestones, or the near-to-mid-term roadmap.
- If a repo provides `PLAN.example.md`, `context/TASK.example.md`, `context/SESSION.example.md`, or `context/MEMORY.example.md`, `init` and `checkpoint` will scaffold missing runtime files from those examples.
- Do not claim completion without running the stated proof path.
- If proof is unavailable, report the work as `blocked` or `incomplete` instead of `done`.
- For Tim Pope style multi-line commit messages, always use a heredoc with
  `EOF` so the commit body contains real line breaks, and never include literal
  `\n` sequences.
- When updating an existing `.prompts/PROMPT_{num}.txt` file, use a commit
  subject prefix of `[UPDATE PROMPT_{num}]` instead of the base prompt prefix.
- Do not add `memory/summaries/` or `memory/sessions/` file entries to
  `memory/INDEX.md`; those directories are gitignored and should only be
  described at the tier level, not indexed file-by-file.

## Verification

Verification scripts use `unittest`, not `pytest`.

```bash
python3 scripts/run_verification.py --tier fast
python3 scripts/validate_context.py
python .acb/scripts/acb_verify.py
```

Context tools (when available):
- `python3 scripts/work.py budget-report --bundle <files>` - scored bundle evaluation
- `python3 scripts/work.py route-check "<prompt>"` - heuristic capability routing
