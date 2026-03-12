# Prompt-First Conventions

Purpose: support repos driven by ordered prompt execution.

Rules:

- Keep prompt numbering strictly monotonic.
- Use explicit file-name references inside prompts.
- Declare deterministic output targets for documentation-heavy prompts.
- Separate system briefs, execution prompts, and meta-runner prompts clearly.

Prevents:

- ambiguous prompt ordering
- lost outputs
- prompt families that cannot be resumed safely
