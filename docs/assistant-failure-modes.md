# Assistant Failure Modes

This repo is designed around repeated assistant failure patterns.

| Failure mode | Typical symptom | Primary mitigation |
| --- | --- | --- |
| Context sprawl | Too many files loaded before the task is narrow | Boot sequence, routers, manifests, and context-loading doctrine |
| Example blending | Several near-match examples get mixed into a new hybrid | Canonical-example priority and example ranking metadata |
| Weak stack inference | The assistant chooses a stack from one filename or keyword | Repo-signal hints, stack router, and prompt-first repo analyzer |
| Unverified progress | Code looks plausible but no boundary was proved | Verification doctrine, example harnesses, and `scripts/run_verification.py` |
| Dev/test contamination | Shared ports, Compose names, or volumes | Compose-isolation doctrine and bootstrap invariant checks |
| Continuity drift | Later sessions have to reconstruct state from scratch | `MEMORY.md`, stop hooks, and handoff snapshots |
| Prompt-first drift | Prompt numbering or references become vague | Prompt-first doctrine and prompt numbering validation |

Add new structure only when a failure mode is recurring enough to justify a durable rule, manifest, example, or tool.
