# Prompt-First Conventions

Prompt-first work should be structured, traceable, and easy to continue later.

## Monotonic Prompt Numbering

When a repo stores prompt files, use strictly monotonic numbering:

- `001-...`
- `002-...`
- `003-...`

Do not renumber old prompts. Do not reuse gaps. If `004` is skipped accidentally, the next prompt is still `005`.

## Explicit Filename References

Prompts should refer to exact repo paths when asking for changes.

Good:

- `Update templates/manifest/manifest.template.yaml`
- `Add tests under tests/integration/test_search_indexing.py`

Bad:

- "fix the manifest template"
- "update the search tests somewhere"

## Prompt Sequence Design

- each prompt should have one dominant goal
- later prompts should build on actual repo state, not assumed state
- prompts should reference previous output by filename when relevant

## Operator Console Workflow

Prompt-first execution uses a two-layer model:

- `.prompts/` defines what each session should do
- `scripts/work.py` manages repo-local runtime continuity between sessions
- any operator-console guidance must match the live repo command set
- the operator drives sequencing; the assistant drives execution

Minimal operator loop:

1. run the live `work.py resume` flow and read runtime state
2. paste the chosen prompt into a fresh session and run the `AGENT.md` boot sequence
3. keep any per-session checklist in `tmp/PROMPT_XX_checklist.md`
4. execute the session and checkpoint normally
5. write `memory/summaries/PROMPT_XX_completion.md` before moving on

## Fresh-Session Boundaries

Prompt files are designed for fresh sessions.

Each prompt should:

- include enough context to boot without depending on a separate hidden system prompt
- reference exact files by path, not only by description
- state its own completion condition explicitly

Do not execute multiple prompt files in one assistant session.

## Pausing And Resuming

When a session stops before completion:

- the operator runs `work.py pause PROMPT_XX.txt --reason "..."`
- the assistant writes `memory/summaries/PROMPT_XX_resume.md`
- the next session reads that resume summary during boot
- broad repo re-reading is unnecessary when the resume summary is complete and current

## Assistant Behavior

Assistants should infer tasks from natural language, but prompt files should still be explicit enough to reduce ambiguity during long-running work.
