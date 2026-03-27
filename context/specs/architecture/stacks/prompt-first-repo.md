---
acb_origin: canonical
acb_source_path: context/specs/architecture/stacks/prompt-first-repo.md
acb_role: architecture
acb_stacks: [prompt-first-repo]
acb_version: 1
---

## Prompt-First Repo Constraints

The repo exists to orchestrate work through profiles, prompts, specs, and validation instructions. Startup order and prompt monotonicity are part of the architecture.

Treat `.acb/` as the local doctrine and profile container, while the visible root stays the operator-facing entry surface.
