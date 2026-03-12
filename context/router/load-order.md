# Load Order

Use this order unless a manifest explicitly overrides it:

1. `README.md`
2. `manifests/repo.profile.yaml`
3. `AGENT.md` or `CLAUDE.md`
4. `context/router/task-routing.md`
5. only the doctrine files directly relevant to the task
6. one workflow file
7. one archetype pack
8. only the necessary stack packs
9. the smallest relevant canonical example set
10. templates only when bootstrapping

Never bulk-load entire directories as a first move.
