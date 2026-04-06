# Startup Trace Protocol

A startup trace is a structured self-declaration written by the assistant at the
end of its boot sequence. It is not automated, not verified, and not a claim
about hidden model state. Its value is making loading decisions inspectable and
forcing intentional declaration.

Write a startup trace when:
- the session loads a substantial context bundle such as a medium profile or larger
- the task spans multiple stacks or workflows
- the operator is debugging a previous session's context load
- `startup_trace_enabled` is true in repo-local `.acb/` config, if that flag exists

Do not write a startup trace when:
- the session is tiny and prompt-only
- the task is a quick status check or one-file fix
- the Session Context Briefing already captures everything needed

Store traces as plain text at:
- `logs/startup/<YYYY-MM-DD-HHMMSS>-trace.md`

Do not use YAML frontmatter. Keep the format explicit and easy to scan.
Startup traces are distinct from Session Context Briefing logs, which end in
`-resume.log`.

Required format:

```text
================================================================
Startup Trace
================================================================
Created:         <ISO datetime>
Session:         <short description of the task or prompt being started>
Entry Point:     <AGENT.md | CLAUDE.md>

Declared Files Read:
  1. <path> — <why loaded>
  2. <path> — <why loaded>

Routers Consulted:
  - <none | router name(s) and what they resolved>

Doctrines Loaded:
  - <doctrine file names, or "none beyond boot sequence">

Memory Artifacts Seen:
  - <memory/summaries/PROMPT_XX_completion.md: present | not present>
  - <context/MEMORY.md: present | missing>

Budget Estimate:
  Files: <N>   Estimated Profile: <tiny|small|medium|large|cross-system|unknown>
  Note: run `work.py budget-report --bundle <files>` for a scored evaluation.

Router Decision:
  Archetype:      <inferred | not applicable>
  Primary Stack:  <inferred | not applicable>
  Workflow:       <selected | not applicable>
  Confidence:     <strong (>= 0.85) | usable | weak | very weak | not declared>

Warnings:
  - <none | list concerns, drift, or missing expected files>
================================================================
```

Anti-patterns:
- copying the Session Context Briefing instead of declaring actual loads
- listing files that were not loaded
- omitting files that were loaded
- inventing router consultations that did not happen

The `Declared Files Read` section is the input to `work.py budget-report`.
After writing a trace, an operator can run:
- `work.py budget-report --bundle <declared-files...>`

This scores the declared bundle against the context budget profiles. The score
reflects the declaration, not proven truth.
