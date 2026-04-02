# PROMPT_90 Completion Summary

## Objective

Enhance `scripts/work.py` to give better practical guidance during fresh-session resume and
checkpoint review, while preserving its role as a simple, assistant-friendly runtime
entrypoint. Specifically:

1. Repo-local example-template scaffolding (`PLAN.example.md`, `context/*.example.md`)
2. Better resume/status signal quality (git anchor, next-step inference, PLAN review hints)
3. Durable-memory promotion hints (heuristics for when `context/MEMORY.md` may deserve updates)
4. Time-aware staleness signals (elapsed-time heuristics for stale session notes)

## Completed

- `scripts/work.py` enhanced with:
  - Repo-local example-template scaffold fallback: `init` and `checkpoint` prefer
    `PLAN.example.md`, `context/TASK.example.md`, `context/SESSION.example.md`,
    `context/MEMORY.example.md` before built-in defaults
  - Last commit timestamp surfaced in `resume` and `status` output
  - "Recent clue" section showing recently changed file paths as resume signals
  - Next-step inference from `context/SESSION.md` and `context/TASK.md`
  - `PLAN.md` review signal: flags if `.prompts` changed after `PLAN.md`, or PLAN is missing
  - Memory-promotion hint: flags when recently changed paths touch assistant-facing docs,
    templates, generator behavior, or prompt doctrine
  - Time-aware staleness: warns when session notes have aged beyond reasonable threshold
- Docs updated to reflect enhanced behavior:
  - `README.md`: added repo-local scaffold examples explanation
  - `AGENT.md`: clarified memory-promotion hint response and checkpoint discipline
  - `CLAUDE.md`: aligned with new scaffold and signal behavior
  - `docs/runtime-state-workflow.md`: documented new signals, scaffold fallback, PLAN doctrine
  - `docs/context-boot-sequence.md`: updated boot order step for `work.py resume`
  - `docs/session-start.md`: aligned with new runtime signals
  - `scripts/README.md`: updated `work.py` documentation
  - `templates/agent-md/AGENT.template.md`: propagated doc updates
  - `templates/claude-md/CLAUDE.template.md`: propagated doc updates
  - `templates/readme/README.template.md`: propagated doc updates
- Verification: `verification/scripts/test_repo_scripts.py` updated to cover new signals
  and scaffold behavior

## Remaining

None.

## Tests Status

`python scripts/run_verification.py --tier fast` — 138 tests total; 6 pre-existing failures
unrelated to PROMPT_90 (test_example_registry_paths_and_levels_are_valid with
`reference` level in `examples/derived/orchestration-strategies.yaml`). These failures
existed before PROMPT_90 started. The new `test_repo_scripts.py` tests covering PROMPT_90
work passed.

`python scripts/validate_context.py` — passed: 27 manifests, context metadata, prompt
numbering, and bootstrap invariants validated.

## Files Touched

- `scripts/work.py`
- `scripts/README.md`
- `README.md`
- `AGENT.md`
- `CLAUDE.md`
- `docs/runtime-state-workflow.md`
- `docs/context-boot-sequence.md`
- `docs/session-start.md`
- `templates/agent-md/AGENT.template.md`
- `templates/claude-md/CLAUDE.template.md`
- `templates/readme/README.template.md`
- `verification/scripts/test_repo_scripts.py`

## Key Commits

- `380a68f` — `[PROMPT_90] enrich work.py runtime resume signals` — core enhancement to
  `scripts/work.py`: repo-local scaffold fallback, git anchor, next-step inference,
  memory-promotion hints, staleness detection
- `9a54b3f` — `[PROMPT_90] document richer runtime workflow signals` — docs aligned to
  new behavior: `README.md`, `AGENT.md`, `CLAUDE.md`, `docs/runtime-state-workflow.md`,
  `docs/context-boot-sequence.md`, `docs/session-start.md`, templates
- `d506082` — `[PROMPT_90] cover work.py signal and scaffold behavior` — verification
  coverage: repo-local example scaffolding, richer resume output, git anchor and next-step
  signal tests

## Pitfalls and Caveats

- The `run_verification.py --tier fast` has 6 pre-existing failures (`reference` level
  invalid in example registry). These predate PROMPT_90 and were not introduced by it.
  Future prompts should investigate or fix the `examples/derived/orchestration-strategies.yaml`
  `reference` level.
- `work.py` remains read-only for `resume` and `status`. Scaffold behavior is conservative:
  only creates missing files, never overwrites existing runtime notes without `--force`.
- The time-aware staleness signal uses heuristics, not real token introspection. It is
  intentionally modest and explainable.
- Memory-promotion hints are suggestions, not forced actions. The assistant must decide
  whether a changed path genuinely deserves a `context/MEMORY.md` update.

## Next Recommended Action

Start PROMPT_91: create the 3-tier committed memory base (`memory/` directory structure
with `INDEX.md`, `concepts/`, `sessions/`, `summaries/`), add memory-compaction doctrine,
and update AGENT.md / CLAUDE.md to reference `memory/INDEX.md`.

## Created At

2026-04-02
