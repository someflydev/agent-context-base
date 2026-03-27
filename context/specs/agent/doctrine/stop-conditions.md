---
acb_origin: canonical
acb_source_path: context/specs/agent/doctrine/stop-conditions.md
acb_role: agent
acb_doctrines: [stop-conditions]
acb_version: 1
---

## Stop Conditions

Stop or escalate when any of these are ambiguous:

- active stack or runtime surface
- archetype or service ownership
- seam contract or persistence target
- validation path required to prove completion
- startup order or repo-local doctrine after drift

Use explicit outcome language:

- `blocked` when a missing dependency, environment, approval, or decision prevents progress
- `incomplete` when work remains but the next step is still knowable
- `done` only when the changed boundary was both implemented and validated
