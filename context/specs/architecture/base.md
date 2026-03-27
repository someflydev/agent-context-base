---
acb_origin: canonical
acb_source_path: context/specs/architecture/base.md
acb_role: architecture
acb_version: 1
---

## Baseline Architecture Constraints

Structure must stay explicit enough that an assistant can identify the changed boundary, the owning module, and the correct validation path without broad repo scanning.

Architectural truth should make these items concrete:

- owned boundaries and forbidden shortcuts
- allowed transports and persistence seams
- where translation or normalization belongs
- which modules may depend on which other modules
- what must remain testable in isolation
