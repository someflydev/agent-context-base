---
acb_origin: canonical
acb_source_path: context/validation/stacks/prompt-first-repo.md
acb_role: validation
acb_stacks: [prompt-first-repo]
acb_version: 1
---

## Prompt-First Stack Validation

Validate prompt numbering, profile integrity, startup order, and generated repo-local payload files. Prompt-first repos are operationally correct only when the local context surface is coherent and reloadable.

Typical commands:

- `python scripts/validate_repo.py`
- `python .acb/scripts/acb_verify.py`
