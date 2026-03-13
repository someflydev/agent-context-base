# Stop-Hook Guidance

In this system, a stop hook is the small continuity update an assistant performs before pausing after meaningful work.

The goal is not to write a diary. The goal is to preserve enough current state that the next session can resume without re-inventing the task.

Use this guidance with:

- `context/memory/MEMORY.contract.md`
- `context/memory/memory-operating-rules.md`
- `context/memory/handoff-snapshots.md`

## What A Stop Hook Means Here

A stop hook is a short end-of-phase update that captures:

- where the task currently stands
- what was learned or decided
- what remains
- what exact files or validations come next

Most stop hooks only require updating `MEMORY.md`.

Some stop hooks require a handoff snapshot.

Some require both.

## When To Perform A Stop-Hook Update

Perform a stop-hook update when pausing after meaningful progress, especially when:

- you inspected enough architecture to choose a path
- you changed code but have not validated it yet
- tests or smoke checks failed and the failure now shapes the task
- a major subtask completed but the overall task is still open
- the task will continue in a fresh session
- a human or another assistant may pick up next

Skip the stop hook for very small one-pass changes that are already complete and verified.

## How Much To Write

Write the minimum that preserves continuity:

- 3 to 10 bullets for `MEMORY.md` updates in most cases
- 1 short checkpoint summary plus concrete next-file references for handoff snapshots

Do not log every command.

Do not narrate every thought.

Do not duplicate doctrine or copied code.

## Summarize Without Writing A Diary

Good stop-hook summaries record:

- decisions
- findings
- concrete remaining actions
- exact files to touch next
- validation state

Weak stop-hook summaries record:

- a chronological transcript
- repetitive status filler
- broad future ideas unrelated to the current task

Prefer:

- "FastAPI route shape should follow `app/api/reports.py`; no new router module needed."
- "Smoke test not run yet; next step is `tests/smoke/test_health.py` plus route smoke."

Avoid:

- "First I looked at README, then I looked at AGENT, then I thought about testing..."

## When To Update `MEMORY.md`

Update `MEMORY.md` when the task is still the same task and you need a mutable current-state checkpoint.

Typical cases:

- same session will likely resume later
- fresh session will continue soon
- the task is midstream and not ready for a durable handoff artifact
- the current update mostly changes working set, findings, decisions, or next steps

## When To Create A Handoff Snapshot Instead

Create a handoff snapshot when the pause point is durable and transfer-oriented:

- the task spans multiple sessions or days
- a human will review or continue
- another assistant may continue
- the repo is a derived repo and you want a fixed checkpoint artifact
- the task has enough completed work that a point-in-time record is useful

## When Both Are Appropriate

Do both when:

- you want `MEMORY.md` to stay current for the immediate next session
- and you also want a durable checkpoint for transfer, audit, or repo history

Typical pattern:

1. update `MEMORY.md` with the live current state
2. create a timestamped handoff snapshot for the durable checkpoint
3. add the new handoff path to `MEMORY.md` only if it helps the next session

## Avoiding Drift And Stale Summaries

To prevent memory drift:

- replace completed next steps with the actual new next steps
- remove files that are no longer active
- rewrite stale findings when code or validation changed
- do not keep resolved blockers
- prefer exact paths and exact prompt filenames over vague labels

If the stop hook would mostly append history, rewrite the existing section instead.

## Trigger Matrix

| Situation | Update `MEMORY.md` | Create handoff snapshot | Notes |
| --- | --- | --- | --- |
| Short trivial change completed and verified in one pass | No | No | Avoid overhead when continuity risk is negligible. |
| Medium feature task midstream | Yes | No | Record current objective, working set, findings, and next steps. |
| Interrupted debugging after failed smoke tests | Yes | Usually yes | Use both when the failure state needs durable transfer. |
| Major subtask done, overall task still open | Yes | Optional | Snapshot if a fresh session or another assistant is likely. |
| Stopping after code changes but before tests | Yes | Optional | Include exact validations still pending. |
| Handing off to a fresh assistant session | Yes | Yes | Keep mutable state plus durable checkpoint. |
| Prompt-first prompt-sequence design mid-batch | Yes | Often yes | Reference exact prompt filenames and numbering decisions. |

## Practical Examples

### 1. Stopping After Inspecting Architecture But Before Changing Code

Update `MEMORY.md` with:

- current objective
- inferred stack and archetype
- exact files inspected
- chosen working set
- next step

Do not create a handoff snapshot unless the pause is likely to span sessions or needs transfer.

### 2. Stopping After Making Code Changes But Before Tests

Update `MEMORY.md` with:

- touched files
- what changed
- validation still pending
- next smoke or integration check

Create a handoff snapshot if the changes are substantial or another session will continue.

### 3. Stopping After Tests Fail

Update `MEMORY.md` with:

- exact failing command or validation surface
- concrete error theme
- suspected boundary
- next files to inspect

Create a handoff snapshot when the failure state itself is important for the next session.

### 4. Stopping After A Major Subtask Is Complete

Update `MEMORY.md` by pruning completed steps and rewriting the next phase.

Create a handoff snapshot if the completed subtask is a meaningful transition point, such as:

- architecture inspection finished
- code generation batch finished
- smoke-test hardening finished
- prompt batch finished

### 5. Stopping Before Handing Off To A Fresh Session

Do both:

- update `MEMORY.md` so the repo carries the live current state
- create a handoff snapshot so the transfer is durable and timestamped

The handoff snapshot should name:

- what is complete
- what remains
- blockers or risks
- exact files to inspect next
- validation status
