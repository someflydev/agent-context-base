# Runtime State Workflow

This repo uses a small repo-local runtime workflow so a fresh assistant session can restart from visible state instead of vague memory.

## Primary Command

Run:

```bash
python3 scripts/work.py resume
```

In compact derived repos that intentionally have no root `scripts/` directory, use the vendored equivalent:

```bash
python3 .acb/scripts/work.py resume
```

The same tool also supports:

```bash
python3 scripts/work.py init
python3 scripts/work.py status
python3 scripts/work.py checkpoint
```

## Canonical Runtime Files

- `PLAN.md`: milestone-level roadmap, major phases, and near-to-mid-term structure. Update it when a `.prompts` megaprompt or major decision materially reshapes milestones or phases. Do not touch it for normal progress inside an already-defined phase.
- `context/TASK.md`: the current active slice. Keep scope, success criteria, immediate steps, blockers, and out-of-scope boundaries concrete.
- `context/SESSION.md`: compact working state for the next session. Record current status, recent decisions, active files, the next safe step, and what does not need to be reloaded.
- `context/MEMORY.md`: durable repo-local truths, recurring guardrails, stable commands, and known pitfalls. Do not let it accumulate temporary task sludge.

These files are runtime state, not doctrine. They should normally stay ignored and local to the working copy.

## Boot Sequence

1. Read `AGENT.md`.
2. Run `python3 scripts/work.py resume`.
3. Read `context/TASK.md`.
4. Read `context/SESSION.md`.
5. Read `context/MEMORY.md` only if durable repo-local truths matter.
6. Read `PLAN.md` when milestone context matters.
7. Continue into `.acb/` startup files in generated repos when the task needs manifest, spec, or validation context.

## Why Heuristics, Not Token Introspection

Subscription coding assistants usually do not expose trustworthy live context-window usage. This workflow treats "active context is too large" as a repo-local, visible condition instead:

- runtime files are too long in lines or words
- `context/SESSION.md` has no clear next safe step
- `context/TASK.md` is stale relative to the active changed-file surface
- too many files changed since the last useful checkpoint
- `context/MEMORY.md` contains temporary, task-local notes
- `.prompts/` changed after `PLAN.md`, so the roadmap may need review

`scripts/work.py` reports those conditions; it does not pretend to know model internals.

## Checkpoint Doctrine

Run `python3 scripts/work.py checkpoint`:

- after meaningful code or doc changes
- after a completed subtask
- after a major test milestone
- before ending a session
- before switching branches or worktrees
- before a likely handoff to a fresh assistant session
- when `context/SESSION.md` is stale, broad, or missing a next safe step
- when a `.prompts` megaprompt materially changes the phase structure

`checkpoint` is intentionally conservative. It scaffolds missing runtime files and reports drift or compaction pressure, but it does not invent task content or rewrite human notes.

## Relationship To Doctrine

- committed docs, manifests, `.acb/` specs, and canonical examples remain the durable doctrine surface
- runtime markdown files are local continuation state
- `.prompts` shape future work, but they only force a `PLAN.md` update when they materially reshape the roadmap
