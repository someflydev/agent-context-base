# Memory Layer Overview

The memory layer adds a small operational continuity surface to the existing `agent-context-base` architecture.

It does not replace doctrine, manifests, examples, code, or the operating manual.

It exists to reduce mid-task context loss in the real workflows this ecosystem supports:

- long coding sessions
- fresh assistant sessions
- interrupted implementation work
- prompt-first repo evolution across multiple prompt runs
- human and assistant handoffs
- derived repos that grow over many sessions

## Section 1 - Why This Architecture Benefits From A Runtime Memory Layer

The existing system already narrows context well:

- routers infer the dominant path
- manifests define bounded context bundles
- doctrine constrains behavior
- examples shape implementation patterns

What it does not preserve by itself is live task state.

That gap shows up in practice when a session pauses midstream:

- the current objective becomes fuzzy
- already inspected files get rescanned
- decisions and rejected options get forgotten
- the next step gets invented from scratch
- prompt-first repo work loses filename-precise continuity

The memory layer solves that specific operational problem.

## Section 2 - Distinctions Between The Layers

Use these distinctions consistently:

- doctrine = stable rules
- manifests = structured context selection
- examples = preferred implementation patterns
- memory = current operational state
- handoff snapshot = durable point-in-time transition artifact

More explicitly:

- doctrine tells the assistant what must remain true
- manifests tell the assistant what bounded context to load
- examples show the preferred finished shape
- `MEMORY.md` tells the next session where the current task actually stands
- a handoff snapshot preserves a fixed checkpoint for transfer

Memory is therefore a runtime layer, not a policy layer.

## Section 3 - What `MEMORY.md` Is For

`MEMORY.md` is for high-signal current-task continuity.

It should capture:

- current objective
- current stack or archetype inference when relevant
- active working set
- already inspected files
- important findings
- decisions already made
- explicitly not doing
- blockers or risks
- next steps
- stop condition

It should stay small, current, and rewrite-friendly.

## Section 4 - What `MEMORY.md` Is Not For

`MEMORY.md` is not:

- doctrine
- a manifest replacement
- a code summary dump
- a transcript
- a backlog for unrelated future ideas
- a substitute for validation or code inspection

If the information is durable and repo-wide, it belongs somewhere else.

## Section 5 - Why Stop Hooks Matter

Stop hooks matter because many failures happen at pause points, not at initial routing time.

Without a stop hook:

- unfinished work gets remembered loosely
- failures get flattened into vague "tests were weird"
- active files are forgotten
- the next session reloads too much context just to recover state

A stop hook turns the end of a work phase into a deliberate continuity checkpoint.

Usually that means updating `MEMORY.md`.

Sometimes it also means writing a handoff snapshot.

## Section 6 - Why Handoff Snapshots Matter

Handoff snapshots matter when a task crosses a real transition:

- later session
- later prompt run
- different assistant
- human review or takeover
- derived repo checkpoint worth preserving

They give the repo a durable point-in-time transfer artifact without bloating `MEMORY.md`.

## Section 7 - Recommended Repository Additions

This pass adds the memory layer in a bounded structure:

```text
context/
  memory/
    MEMORY.contract.md
    MEMORY.template.md
    stop-hook-guidance.md
    handoff-snapshots.md
    memory-operating-rules.md
docs/
  memory-layer-overview.md
examples/
  canonical-workflows/
    MEMORY.example.md
    HANDOFF-SNAPSHOT.example.md
templates/
  memory/
    MEMORY.template.md
    HANDOFF-SNAPSHOT.template.md
scripts/
  init_memory.py
  create_handoff_snapshot.py
  check_memory_freshness.py
```

This fits cleanly because:

- stable operational guidance lives under `context/memory/`
- repo-wide explanation lives under `docs/`
- realistic examples live under `examples/`
- starter scaffolds for derived repos live under `templates/`
- lightweight helpers live under `scripts/`

## Section 8 - Relationship To Doctrine, Workflows, Manifests, Examples, Code, And The Operating Manual

Memory depends on the existing layers instead of competing with them.

- doctrine still governs policy and stop conditions
- workflows still govern execution sequence
- manifests still govern bounded context loading
- examples still govern preferred implementation patterns
- code and tests still define implementation reality
- the operating manual still explains system behavior

Memory only preserves the current operational checkpoint between those systems and the next session.

## Section 9 - Context Complexity Budget Interaction

The memory layer supports the context complexity budget philosophy because it can act as a compressed checkpoint.

Used well, it reduces:

- unnecessary rescanning
- repeated repo-orientation work
- duplicate inspection of already-settled files
- scope drift caused by forgotten decisions

Used badly, it would become a loophole.

Do not use memory to:

- bypass doctrine
- skip manifest or router logic
- avoid verifying code and tests
- justify loading more unrelated context

The budget benefit is simple: memory can lower reload cost, but it does not increase authority.

## Section 10 - Derived Repo Guidance

Derived repos do not need to commit to heavy process.

Recommended approach:

- use a repo-local `MEMORY.md` when work is likely to span sessions
- initialize it at the start of a non-trivial task or the first meaningful pause point
- keep it at the repo root for discoverability
- use `artifacts/handoffs/` for durable transfer artifacts when needed
- keep lightweight repos lightweight; not every tiny task needs a snapshot

Disciplined usage becomes more useful when:

- the repo is prompt-first
- the repo evolves through many assistant sessions
- the task touches deployment or smoke-test checkpoints
- multiple humans or assistants collaborate

## Section 11 - Prompt-First Repo Compatibility

Prompt-first repos need filename-precise continuity.

The memory layer should capture:

- which prompt files were completed
- the next intended prompt filename
- prompt numbering decisions already made
- prompts deliberately deferred or not created

Use exact filenames such as:

- `.prompts/003-add-memory-layer.txt`
- `.prompts/004-refine-memory-scripts.txt`

Do not record prompt status vaguely.

For one prompt run per session, then quit, then resume later:

- update `MEMORY.md` at the end of the run
- create a handoff snapshot when the run produced meaningful progress or unresolved validation state

This pattern preserves monotonic numbering discipline without forcing the next session to reconstruct prompt history from scratch.
