---
acb_origin: canonical
acb_source_path: context/specs/agent/base.md
acb_role: agent
acb_version: 1
---

## Baseline Agent Operating Rules

Agents may act autonomously only within explicit constraints. Specs define what must be true; validation defines how truth is proved.

The default operating rhythm is:

1. rehydrate the local context
2. identify one active boundary
3. plan the validation path before coding
4. implement one reviewable slice
5. run the relevant checks
6. update continuity artifacts only when the truth changed

Required session behavior:

- re-read the repo-local `.acb/` startup files at the beginning of every new session
- name the validation path before coding when the changed boundary is not trivial
- do not claim completion until the relevant checks actually ran
- if proof is blocked, say `blocked`; if work remains without proof, say `incomplete`; say `done` only after proof
