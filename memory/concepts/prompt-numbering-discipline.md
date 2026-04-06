# Concept: Prompt Numbering Discipline

Prompt numbering is strict and monotonic in `.prompts/`.

- Never reuse a prompt number.
- Never insert a new prompt below the current highest number.
- Check the highest existing `PROMPT_XX.txt` before creating a new prompt.
- Use exact filenames such as `PROMPT_95.txt`, not descriptive aliases.
- Keep cross-references pointed at real prompt filenames.
- Treat template companions like `PROMPT_11_t.txt` as attached to one numbered step.
- Do not assume historical notes are current; inspect the live prompt tree first.

Fast check:

- Run `rg --files .prompts`
- Sort by filename
- Confirm the highest numbered prompt before choosing the next slot

_Last updated: 2026-04-05_
