# Concepts

Durable knowledge unlikely to change session-to-session.

## What Belongs Here

- Stable conventions not obvious from reading code
- Architectural decisions whose rationale is not in comments or doctrine
- Known recurring pitfalls that have caused confusion more than once
- Patterns that surfaced in multiple sessions and are likely to surface again
- Decisions about prompt sequencing, numbering discipline, or generation behavior

## What Does NOT Belong Here

- Active task state → `context/TASK.md`
- Session logs or exploration notes → `memory/sessions/`
- Prompt-boundary checkpoint summaries → `memory/summaries/`
- Policy and rules → `context/doctrine/`
- Ephemeral working notes → `context/MEMORY.md`

## File Format Convention

- Filename: kebab-case descriptive slug — e.g., `prompt-numbering-discipline.md`
- Header: `# Concept: <Title>`
- Body: dense, fact-first, no padding
- Final line: `_Last updated: YYYY-MM-DD_`

## When To Create A New Concept File

- After the second time you look something up and wish it were written down
- After resolving a non-obvious confusion that affected implementation
- After a session that produced a durable finding worth preserving across prompts
- Do NOT create a concept file for things you only expect to need once
