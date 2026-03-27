---
acb_origin: canonical
acb_source_path: context/specs/agent/doctrine/startup-rehydration.md
acb_role: agent
acb_doctrines: [startup-rehydration]
acb_version: 1
---

## Startup And Rehydration

Future sessions should be able to recover the repo shape from `.acb/SESSION_BOOT.md`, `.acb/profile/selection.json`, the synthesized spec files, and the generated profile. Do not force broad rediscovery of the repo.

When startup truth changes, refresh the local `.acb` payload or the generated profile before asking a later session to continue.

Session start order matters:

- re-read `.acb/SESSION_BOOT.md`, `.acb/profile/selection.json`, `.acb/specs/AGENT_RULES.md`, and `.acb/specs/VALIDATION.md`
- check `.acb/validation/CHECKLIST.md` and `.acb/validation/COVERAGE.md` before assuming prior proof expectations still hold
- treat `MEMORY.md` as continuity only after the stable `.acb/` surface was rehydrated
