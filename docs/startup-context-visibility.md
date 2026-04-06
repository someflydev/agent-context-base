# Startup Context Visibility

This repo makes session startup visible instead of implicit.

Without explicit startup logging, a fresh assistant session is opaque. It is
hard to tell what runtime files existed, whether the repo state was clean, what
the complexity posture looked like, or whether a relevant memory summary was
available when the session began.

The startup visibility model solves that with three levels.

## Three-Level Visibility Model

### Level 1: Session Context Briefing

`python3 scripts/work.py resume` prints a Session Context Briefing at the top of
every fresh-session startup.

It shows:

- current local date and time
- repo root, branch, and HEAD anchor
- working-tree cleanliness or changed-file breadth
- presence and size of `PLAN.md`, `context/TASK.md`, `context/SESSION.md`, and
  `context/MEMORY.md`
- presence of `memory/INDEX.md`
- count of `memory/summaries/*.md`
- the most relevant recent summary, if one is found from prompt-prefixed git
  history
- total runtime-note line count and the lean or moderate or heavy posture
- whether `tmp/*.md` currently has an active checklist
- one recommended next action

This briefing is available in every session and reflects actual file presence at
the moment `resume` is run.

### Level 2: Startup Log

`python3 scripts/work.py resume --write-startup-log` writes the same Session
Context Briefing to `logs/startup/<timestamp>-resume.log`.

This level is optional. It exists for after-the-fact review when an operator
needs to confirm how a session started or debug context-loading decisions.

### Level 3: Startup Trace

`python3 scripts/work.py startup-trace write` writes a self-declared startup
trace to `logs/startup/<timestamp>-trace.md`.

It shows:

- what the assistant says it loaded during boot
- why those files were declared
- which doctrines or routers were consulted
- what memory artifacts were seen
- the estimated budget profile for the declared bundle

This level is optional. It is not automated and not verified. Its purpose is to
make declared loading discipline inspectable and reviewable after the fact.

## How To Use It

- Always run `python3 scripts/work.py resume` first in a fresh session.
- Read the Session Context Briefing before loading task-specific context.
- If the complexity budget is heavy, prune runtime notes before broad loading.
- If quota is not ready in the operator console, wait or use a different
  assistant path.
- If a relevant memory summary exists, load it before deeper repo exploration.
- Use the recommended-next-action line as the default startup move unless the
  task clearly requires a narrower path.
- For medium or larger sessions, multi-stack tasks, debugging sessions, or
  when the operator wants a scored audit of loading discipline, write a startup
  trace after boot.

## Interpretation Guide

- `lean`: fewer than 200 total runtime-note lines. Normal startup. Continue with
  the usual boot sequence.
- `moderate`: 200 to 400 total runtime-note lines. Still workable. Read
  selectively and avoid loading extra context too early.
- `heavy`: more than 400 total runtime-note lines. Prune `context/TASK.md` or
  `context/SESSION.md` before expanding the session further.

The posture is heuristic, not a token measurement. It exists to keep runtime
state readable and compact for the next assistant session.

## Integration With `memory/` And `work.py`

Level 1 is the synthesis point for actual repo state at session start. Level 2
persists that same state for review. Level 3 records what the assistant
declares it loaded and can be scored later with `work.py budget-report`.

`work.py resume` remains the normal assistant entrypoint. The visibility layer
does not invent hidden state; it makes startup state and declared loading
discipline explicit and reviewable.
