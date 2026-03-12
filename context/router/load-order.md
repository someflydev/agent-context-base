# Load Order

Use this order unless a manifest explicitly overrides it:

1. `README.md`
2. `manifests/repo.profile.yaml`
3. `AGENT.md` or `CLAUDE.md`
4. `context/router/task-router.md`
5. `context/router/stack-router.md` only if the stack is unclear
6. `context/router/archetype-router.md` only if the archetype is unclear
7. only the doctrine files directly relevant to the task
8. one workflow file
9. one archetype pack
10. only the necessary stack packs
11. the smallest relevant canonical example set
12. templates only when bootstrapping

Never bulk-load entire directories as a first move.
