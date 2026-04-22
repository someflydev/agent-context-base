# work.py graft

## Purpose
Install the ACB session discipline into an existing locally cloned repo.

## Usage
    python3 scripts/work.py graft /path/to/target-repo [--dry-run] [--force] [--no-prompts]

## What it installs

| File/Directory | Purpose |
|----------------|---------|
| `scripts/work.py` | ACB session management tool |
| `memory/` | Memory root directory |
| `memory/INDEX.md` | Memory index — promote durable findings here |
| `memory/concepts/` | Memory concepts tier |
| `memory/summaries/` | Memory summaries tier |
| `memory/sessions/` | Memory sessions tier |
| `context/` | Runtime context root |
| `context/TASK.md` | Active task runtime file |
| `context/SESSION.md` | Session runtime file |
| `context/MEMORY.md` | Durable repo-local memory (gitignored by convention) |
| `CLAUDE.md` | Assistant boot entrypoint |
| `AGENT.md` | Assistant operating rules |
| `.prompts/` | Prompt-first workflow directory (unless `--no-prompts`) |
| `.prompts/analyze-and-reverse-engineer.txt` | Starter analysis prompt (unless `--no-prompts`) |

## What it does NOT install

- Stack definitions, archetypes, or canonical examples
- Verification suites or agent-context-base-specific docs
- `.prompts/` megaprompts beyond the analysis template
- Any content specific to the agent-context-base repo

## .gitignore entries (add manually after grafting)

    work/
    PLAN.md
    context/MEMORY.md

## Workflow after grafting

1. Review the grafted files
2. Add the `.gitignore` entries above
3. Commit the grafted files with deliberate staging and a multi-line message
4. Open a session in the target repo
5. Run: `python3 scripts/work.py resume`
6. Run the analysis prompt: `cat .prompts/analyze-and-reverse-engineer.txt`

## The analyze-and-reverse-engineer prompt

A self-contained prompt for a fresh assistant session in a newly-grafted repo.
Running it causes the assistant to analyze the codebase deeply and produce:
a populated `context/TASK.md`, a `context/SESSION.md`, an optional `PLAN.md`
(only when roadmap-level tracking is warranted), a starter promptset in
`.prompts/PROMPT_01.txt` through `PROMPT_NN.txt`, and a summary at
`memory/summaries/PROMPT_00_analysis.md`. Run it once, immediately after
grafting, to orient the codebase and generate a promptset rooted in the repo's
actual domain and technical shape.
