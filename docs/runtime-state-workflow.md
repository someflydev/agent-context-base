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

Some repos also expose an operator-console layer through the same script, such as:

```bash
python3 scripts/work.py init-project
python3 scripts/work.py next
python3 scripts/work.py start PROMPT_XX.txt --assistant codex
python3 scripts/work.py pause PROMPT_XX.txt --reason "..."
python3 scripts/work.py done PROMPT_XX.txt
python3 scripts/work.py verify
python3 scripts/work.py recent-commits
python3 scripts/work.py log-quota --assistant claude --used-pct-5h 45
```

`resume` and `status` stay read-only. `checkpoint` and `init` may scaffold missing files, but they do not silently replace existing runtime notes unless `--force` is used.

Operator-console commands should be documented from the live repo command set, not
from historical assumptions about what `work.py` might provide.

Additional validation commands, when enabled in the current repo:

```bash
python3 scripts/work.py budget-report --bundle <files>
python3 scripts/work.py startup-trace write --session "<task>" --files <files>
python3 scripts/work.py route-check "<prompt>"
```

See `docs/startup-context-visibility.md` for when and how to use these.

## Canonical Runtime Files

- `PLAN.md`: milestone-level roadmap, major phases, and near-to-mid-term structure. Update it when a `.prompts` megaprompt or major decision materially reshapes milestones or phases. Do not touch it for normal progress inside an already-defined phase.
- `context/TASK.md`: the current active slice. Keep scope, success criteria, immediate steps, blockers, and out-of-scope boundaries concrete.
- `context/SESSION.md`: compact working state for the next session. Record current status, recent decisions, active files, the next safe step, and what does not need to be reloaded.
- `context/MEMORY.md`: durable repo-local truths, recurring guardrails, stable commands, and known pitfalls. Do not let it accumulate temporary task sludge.
- `tmp/*.md`: optional local checklists or ad hoc execution plans for the current session. Keep them concise and do not treat them as roadmap state.

These files are runtime state, not doctrine. They should normally stay ignored and local to the working copy.

Within that model, `tmp/*.md` is the session-scoped scratch layer:

- use `PLAN.md` for roadmap-level phases and milestones
- use `context/TASK.md` for the active slice
- use `context/SESSION.md` for the next safe step
- use `context/MEMORY.md` for durable local repo truths
- use `tmp/*.md` for ad hoc checklists and short-lived execution plans

Do not use `tmp/*.md` as a second roadmap or as a replacement for prompt-boundary
summaries.

## Two-Layer Model

This repo separates operator sequencing from assistant execution.

- The operator manages queue state, prompt progression, and any `work.py` operator-console commands that exist.
- The assistant uses boot docs, `work.py resume`, runtime notes, and memory summaries to execute one bounded session.
- `.prompts/` defines what a session should do; runtime files and `work.py` carry continuity between sessions.

When the operator-console layer exists, it is still an operator tool. The
assistant should begin with the normal boot sequence before implementation work.

## Repo-Local Scaffold Examples

When scaffolding a missing runtime file, `scripts/work.py` now prefers a repo-local example file with the matching `*.example.md` name:

- `PLAN.example.md` -> `PLAN.md`
- `context/TASK.example.md` -> `context/TASK.md`
- `context/SESSION.example.md` -> `context/SESSION.md`
- `context/MEMORY.example.md` -> `context/MEMORY.md`

If the example file is absent, the tool falls back to its built-in default scaffold. This keeps the workflow deterministic while still letting a repo customize its own runtime-note starting shape.

## Boot Sequence

1. Read `AGENT.md`.
2. Run `python3 scripts/work.py resume`.
3. Read `context/TASK.md`.
4. Read `context/SESSION.md`.
5. Read `context/MEMORY.md` only if durable repo-local truths matter.
6. Read `PLAN.md` when milestone context matters.
7. Read `tmp/*.md` only when there is an active local checklist or ad hoc session plan relevant to the task.
8. Continue into `.acb/` startup files in generated repos when the task needs manifest, spec, or validation context.

`resume` should give a fresh assistant a grounded snapshot first: current branch and working-tree breadth, the latest commit anchor, recent changed-file clues, the best visible next step from `context/SESSION.md` or `context/TASK.md`, whether `PLAN.md` likely deserves review, and whether recent work looks like it may deserve promotion into `context/MEMORY.md`.

## Why Heuristics, Not Token Introspection

Subscription coding assistants usually do not expose trustworthy live context-window usage. This workflow treats "active context is too large" as a repo-local, visible condition instead:

- runtime files are too long in lines or words
- `context/SESSION.md` has no clear next safe step
- `context/TASK.md` or `context/SESSION.md` simply aged long enough to deserve review
- `context/TASK.md` is stale relative to the active changed-file surface
- too many files changed since the last useful checkpoint
- `context/MEMORY.md` contains temporary, task-local notes
- `.prompts/` changed after `PLAN.md`, so the roadmap may need review
- recent changed paths suggest a durable-memory promotion may be warranted

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

When `checkpoint` or `status` hints that `context/MEMORY.md` may need promotion, treat that as a prompt to review whether the change introduced a stable new rule, repo truth, pitfall, or reusable command. Do not copy active task notes into memory just because files changed.

## Relationship To Doctrine

- committed docs, manifests, `.acb/` specs, and canonical examples remain the durable doctrine surface
- runtime markdown files are local continuation state
- `tmp/*.md` is the right place for prompt-session checklists or one-off action plans
- `.prompts` shape future work, but they only force a `PLAN.md` update when they materially reshape the roadmap
