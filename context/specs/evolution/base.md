---
acb_origin: canonical
acb_source_path: context/specs/evolution/base.md
acb_role: evolution
acb_version: 1
---

## Safe Evolution Rules

New features should extend the existing spec and validation model instead of bypassing it. Every meaningful change should preserve or refine:

- owned boundaries
- validation gates
- startup order
- repo-local operator guidance

Spec drift is a real defect because it makes future autonomy unsafe.
