# Manage Work Queue

Use this workflow to manage the repo-local `work.py` operator-console queue.

## 1. Initialize The Operator Console

Action:

1. run `python3 scripts/work.py init-project`
2. confirm the repo now has `work/WORK_STATE.json` and the generated queue files
3. rerun with `--force` only when you intend to replace existing operator-console state

Use this when starting prompt-first tracking for a repo that does not yet have a
local queue.

## 2. View The Queue And Repo Readiness

Action:

1. run `python3 scripts/work.py next`
2. read the next prompt, quota status, and any resume-summary signal
3. run `python3 scripts/work.py verify` to check queue consistency and local operator state

Use `next` for "what should happen now" and `verify` for "is the local queue healthy."

## 3. Add Prompts To The Queue

Action:

1. prefer `python3 scripts/work.py init-project` when initializing queue structure from the repo's prompt set
2. if you need to add or adjust entries later, edit `work/WORK_STATE.json` directly
3. keep prompt filenames exact, for example `PROMPT_93.txt`
4. preserve status values and prompt ordering consistency

There is no dedicated queue-add command yet. Treat direct `WORK_STATE.json`
editing as the current manual maintenance path.

## 4. Start A Session

Action:

1. choose the prompt file you intend to execute
2. run `python3 scripts/work.py start PROMPT_XX.txt --assistant ASSISTANT`
3. open a fresh assistant session
4. run the repo boot sequence and execute only that prompt

Use a real assistant label, for example `codex` or `claude`, so the run history
is useful later.

## 5. Pause A Session

Action:

1. stop at a clean boundary when possible
2. run `python3 scripts/work.py pause PROMPT_XX.txt --reason "why the session stopped"`
3. write `memory/summaries/PROMPT_XX_resume.md`
4. include the next safe step and current verification state

Pause when quota, time, blockers, or context pressure prevent safe completion in
the current session.

## 6. Complete A Session

Action:

1. finish implementation and required verification
2. run `python3 scripts/work.py done PROMPT_XX.txt`
3. write `memory/summaries/PROMPT_XX_completion.md`
4. confirm the queue now reflects the completed prompt accurately

Do not mark a prompt done before its stated completion condition is actually met.

## 7. Log Quota State

Action:

1. gather the current quota reading for the relevant assistant
2. run `python3 scripts/work.py log-quota --assistant claude --used-pct-5h 45`
3. include any additional supported quota fields when you have them
4. rerun `python3 scripts/work.py next` if you want a readiness check after logging

Use quota logging to make start decisions visible instead of relying on memory.

## 8. Review Recent Prompt Commits

Action:

1. run `python3 scripts/work.py recent-commits`
2. scan the recent prompt-prefixed history
3. compare commit subjects against queue status if something looks inconsistent

Use this when you need a quick prompt-history view without reconstructing it by
hand from `git log`.

## 9. Judge Queue Health

Good state looks like:

- `work/WORK_STATE.json` exists and parses cleanly
- prompt filenames match files under `.prompts/`
- statuses reflect reality (`pending`, `in_progress`, `paused`, `done`)
- recent run history entries line up with start/pause/done events
- quota state is current enough to make a start decision
- the next prompt and any resume summary are easy to identify

Degraded state looks like:

- missing `WORK_STATE.json`
- queue entries for prompt files that no longer exist
- duplicate or contradictory statuses
- a paused prompt with no resume summary
- a prompt marked done without matching completion notes or commit evidence
- stale quota data blocking a confident start decision

When the queue is degraded:

1. run `python3 scripts/work.py verify`
2. repair `work/WORK_STATE.json` or rerun `init-project` if the state is beyond easy manual repair
3. only start the next prompt after the queue and summaries are coherent again
