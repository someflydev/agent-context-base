# Handoff Snapshots

A handoff snapshot is a durable point-in-time transfer artifact for meaningful pauses.

It is not the same thing as `MEMORY.md`.

`MEMORY.md` is mutable current state.

A handoff snapshot records a fixed checkpoint that another human or assistant can resume from later.

## Why Handoff Snapshots Matter

Long tasks often outlive a single session.

Fresh sessions also lose the invisible context that used to live only in the prior assistant's working memory:

- why a path was chosen
- what was already verified
- what was ruled out
- which exact files should be inspected next

Snapshots make those transitions explicit without forcing `MEMORY.md` to become an archive.

## How A Snapshot Differs From `MEMORY.md`

`MEMORY.md`:

- mutable
- focused on the current live task state
- rewritten as the task evolves
- usually one file per repo

Handoff snapshot:

- immutable once written
- captures one durable checkpoint
- suited for transfer across sessions or assistants
- can exist as a sequence of timestamped artifacts

## When A Mutable `MEMORY.md` Is Enough

`MEMORY.md` alone is usually enough when:

- the task is short
- the same assistant session is likely to resume soon
- no meaningful checkpoint needs to be preserved
- the repo is in a quick prompt-run cycle and the work has not yet crossed a major boundary

## When A Snapshot Is Recommended

Use a handoff snapshot when:

- the task spans multiple sessions
- the work was interrupted after meaningful progress
- another assistant or a human is likely to continue
- a derived repo is evolving over many prompt runs
- a major subtask is complete and the next phase should start from a clean checkpoint
- failed smoke tests, deploy checks, or integration checks need to be preserved accurately

## When It Is Overkill

Do not create a snapshot for:

- tiny one-file edits completed in one pass
- trivial typo fixes
- fully completed and verified small tasks
- pauses where `MEMORY.md` already captures everything needed and there is no realistic handoff risk

## Recommended Paths

Preferred default:

- `artifacts/handoffs/`

Acceptable lightweight alternative:

- `handoffs/`

Use one convention consistently per repo.

`artifacts/handoffs/` is preferred when the repo already separates generated or operational artifacts from durable docs.

## Naming Convention

Use timestamped filenames with a short slug:

- `2026-03-12-154500-memory-layer-pass.md`
- `2026-03-12-221000-fastapi-report-endpoint.md`
- `2026-03-13-090000-prompt-batch-003-004.md`

Good names:

- sort naturally
- remain human-readable
- indicate the checkpoint theme

## Minimal Required Contents

A useful handoff snapshot should contain:

- title
- timestamp
- task or objective
- current repo context such as stack, archetype, manifest, or prompt batch when relevant
- completed work
- remaining work
- blockers or risks
- exact files to inspect next
- validation, smoke-test, or deploy status

Optional but useful:

- current `MEMORY.md` summary excerpt
- exact prompt filenames
- recent handoff predecessor if this is part of a chain

## Referencing Concrete Files And State

Snapshots should reference:

- exact file paths
- exact prompt filenames
- exact validations run or not run
- exact deployment or smoke boundaries affected

Avoid vague phrases such as:

- "the routing file"
- "the next prompt"
- "the tests"

Prefer:

- `context/memory/stop-hook-guidance.md`
- `.prompts/004-refine-memory-scripts.txt`
- `python scripts/check_memory_freshness.py --strict`

## Derived Repo Guidance

Derived repos should adopt snapshots selectively, not mechanically.

Recommended usage:

- prompt-first repos that evolve over many sessions should use snapshots at major prompt boundaries
- services with deployment or smoke-test checkpoints should snapshot meaningful partial progress
- quick single-session tasks usually need only `MEMORY.md`

For the common pattern of one prompt run, quit, then fresh session later:

- keep `MEMORY.md` current at the end of the run
- write a handoff snapshot when the run produced meaningful progress or unresolved validation state

## Suggested Workflow

1. update `MEMORY.md`
2. create a timestamped handoff snapshot
3. include exact files to inspect next
4. include validation status
5. prune `MEMORY.md` so it stays current instead of archival

Use `scripts/create_handoff_snapshot.py` when a lightweight helper is useful.
