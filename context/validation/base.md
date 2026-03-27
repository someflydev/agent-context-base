---
acb_origin: canonical
acb_source_path: context/validation/base.md
acb_role: validation
acb_version: 1
---

## Baseline Validation Contract

Validation describes how truth is checked, not how success is narrated. Every slice should identify the smallest real proof command set that demonstrates the changed boundary.

Minimum expectations:

- a direct changed-boundary proof
- a startup or readiness proof when processes changed
- an operator-readable failure mode when prerequisites are missing
- updated validation notes when the expected proof path changed

Each validation plan should make four things visible:

- the command or harness to run
- the success condition
- the failure condition
- the prerequisite or environment assumption that can block the check
