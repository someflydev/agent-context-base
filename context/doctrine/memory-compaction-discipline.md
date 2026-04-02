# Memory Compaction Discipline

## Compaction Defined

Compaction in this repo is explicit, file-based, and inspectable. It is not hidden
automation. It means deliberately summarizing session state into a persistent artifact at
a meaningful boundary — a completed prompt, a mid-prompt pause, a major decision point.
The result is a committed file, not a side-effect.

## The 3-Tier Memory Structure

```
context/MEMORY.md          local, gitignored, mutable, current-task-scoped
memory/concepts/           committed, durable knowledge, grows slowly
memory/sessions/           committed, session logs, prompt execution notes
memory/summaries/          committed, prompt-boundary checkpoints, resume handoffs
artifacts/handoffs/        committed, general timestamped transfer snapshots (unchanged)
```

Each tier serves a different consumer and lifespan:

- `context/MEMORY.md`: the live layer — updated constantly during a session, pruned
  aggressively, never archival
- `memory/summaries/`: the checkpoint layer — written at prompt boundaries, immutable once
  committed, primary resume artifact for fresh sessions
- `memory/concepts/`: the durable-knowledge layer — written when a finding will recur,
  rarely changed, fact-first
- `memory/sessions/`: the trace layer — written when exploration produced non-obvious
  results not suited for concepts

## Compaction Triggers

An assistant should write a compaction artifact when:

| Condition | Artifact |
|-----------|----------|
| A prompt is paused mid-execution | `memory/summaries/PROMPT_XX_resume.md` |
| A prompt completes | `memory/summaries/PROMPT_XX_completion.md` |
| A non-obvious finding was resolved and will come up again | `memory/concepts/<slug>.md` |
| `context/MEMORY.md` is bloated with stale sections | Prune MEMORY.md; promote stable findings to concepts/ |
| A substantial exploration session produced reusable knowledge | `memory/sessions/<date>-<slug>.md` |

## Prompt-Boundary Convention

After every completed or paused prompt, a summary artifact should be placed in
`memory/summaries/`. This is the primary source for fresh sessions resuming that work.
The summary must use real data — real commit hashes, real file paths, real test output.
No placeholders.

Filename patterns:
- `PROMPT_XX_completion.md` — written when the prompt is fully done
- `PROMPT_XX_resume.md` — written when the prompt is paused mid-execution

## Anti-Patterns

- Writing summaries that are just `context/MEMORY.md` copies with different names
- Growing `memory/sessions/` without ever promoting findings to `memory/concepts/`
- Treating `memory/` as a backup of `context/MEMORY.md`
- Creating summaries that reference placeholder text or `<TODO>` markers
- Writing compaction artifacts speculatively — only write them at real boundaries
- Using `memory/concepts/` for one-off findings unlikely to recur

## Integration with `work.py`

`work.py checkpoint` and `work.py resume` will reference `memory/summaries/` in a future
prompt (PROMPT_92). This doctrine establishes the conceptual contract: summaries are the
primary resume artifact, concepts are durable knowledge, and the local `context/MEMORY.md`
remains the live task state. The tool should surface relevant summaries during resume
rather than requiring the assistant to discover them manually.
