---
acb_origin: canonical
acb_source_path: context/specs/agent/doctrine/testing-philosophy.md
acb_role: agent
acb_doctrines: [testing-philosophy]
acb_version: 1
---

## Testing And Verification Discipline

Prefer proof of the changed boundary over blanket test volume. The right check is the smallest real check that demonstrates the intended truth and exposes likely regressions.

Narrative specs and validation plans must stay aligned. When behavior changes, update both in the same slice.

Proof should stay runnable by a later unattended session:

- state the exact command or harness when practical
- name the expected success condition
- note the real failure mode or missing prerequisite when the proof path cannot run
