# Checkpoint And Resume

Use this workflow to stop and restart prompt-first work without losing the next
safe step.

## 1. Decide When A Summary Is Required

Action:

1. write a resume summary when a prompt stops before completion
2. write a completion summary when a prompt finishes
3. do this at prompt boundaries, not only when a session felt long

If the next session would otherwise need to rediscover scope, files, or
verification state, write the summary.

## 2. Write `memory/summaries/PROMPT_XX_resume.md`

Action:

1. create `memory/summaries/PROMPT_XX_resume.md`
2. include the active prompt file and why execution stopped
3. list the files changed or inspected
4. record decisions already made
5. record verification run, skipped, blocked, or still pending
6. end with one exact next safe step

Required sections:

- active prompt
- current status
- changed or relevant files
- decisions
- verification state
- next safe step
- blockers or risks

Write this immediately after pausing, while the working state is still fresh.

## 3. Write `memory/summaries/PROMPT_XX_completion.md`

Action:

1. create `memory/summaries/PROMPT_XX_completion.md`
2. summarize what the prompt changed
3. list the final artifact files
4. record verification that passed, was not applicable, or remains blocked
5. note any follow-up that belongs to a later prompt instead of reopening this one

Required sections:

- completed prompt
- outcome summary
- changed files
- verification
- follow-ups or known gaps

Completion summaries are the default handoff before moving to the next prompt.

## 4. Use A Resume Summary In A Fresh Session

Action:

1. run the normal boot sequence
2. read `memory/summaries/PROMPT_XX_resume.md` before loading broader task context
3. confirm the repo state still matches the summary
4. continue from the recorded next safe step instead of rediscovering the whole repo

If the summary conflicts with current repo signals, reconcile the conflict first
instead of trusting stale notes blindly.

## 5. Promote Durable Findings To `memory/concepts/`

Action:

1. review the pause or completion summary after the prompt settles
2. identify findings that are durable across prompts or sessions
3. promote only those durable findings into `memory/concepts/`
4. keep prompt-specific execution detail in `memory/summaries/`

Promote when the knowledge is reusable doctrine or a stable repo truth, not just
the story of one prompt run.

## 6. Use `artifacts/handoffs/` When The Snapshot Is Broader

Action:

1. choose `artifacts/handoffs/` when the handoff spans more than one prompt
2. use it for broader project snapshots, external operator notes, or timestamped transfer packages
3. keep prompt-boundary execution handoffs in `memory/summaries/`

Do not replace prompt summaries with generic handoff snapshots unless the
handoff is genuinely broader than the prompt boundary.

## 7. Prune Old Summaries Safely

Action:

1. keep the latest useful resume or completion summary for active work
2. remove older summaries only after the prompt is complete and the relevant knowledge is captured elsewhere if needed
3. keep any summary still referenced by a paused queue entry

It is safe to prune when:

- the prompt is done
- no active queue entry depends on the summary
- any durable learning has already been promoted to `memory/concepts/` or committed docs
