# Assistant Failure Modes

This repo is optimized to reduce repeated assistant mistakes, not to pretend they never happen.

## Common Failure Modes

- loading too much context before the task is narrowed
- mixing templates and canonical examples as if they carry the same authority
- inferring a stack from one weak signal instead of the dominant change surface
- changing deployment or storage behavior without defining a verification path
- reusing default ports or shared Compose names across repos
- drifting prompt numbering or repo-profile references over time

## Mitigations In This Repo

- routers plus `docs/session-start.md` keep the first read set small
- `context/doctrine/stop-conditions.md` names the most important pause points
- `context/context-weights.json` favors stable routing and doctrine files over templates
- `examples/catalog.json` ranks canonical examples instead of relying on ad hoc memory
- `context/router/repo-signal-hints.json` and `scripts/prompt_first_repo_analyzer.py` make repo inference inspectable
- `scripts/validate_context.py` checks metadata integrity and bootstrap isolation behavior

## When To Add More Structure

Add a new rule, anchor, or example only when the same failure mode recurs across repos. Do not convert one-off confusion into permanent architecture.
