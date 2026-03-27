---
acb_origin: canonical
acb_source_path: context/specs/architecture/stacks/go-echo.md
acb_role: architecture
acb_stacks: [go-echo]
acb_version: 1
---

## Go + Echo Constraints

Handlers should stay explicit and small. Serialization, validation, and persistence should live behind named functions or packages instead of accumulating in one large handler chain.

Keep transport details separate from domain logic so tests can prove handler behavior and business logic independently.
