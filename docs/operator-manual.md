# Operator Manual

This base repo is meant to be copied into future projects and then trimmed, not expanded into a giant central monorepo.

Operator defaults:

1. Keep `AGENT.md` and `CLAUDE.md` short.
2. Update `manifests/repo.profile.yaml` before expanding stack docs.
3. Add a canonical example before adding a second prose explanation for the same pattern.
4. When adding Docker-backed infra, preserve `docker-compose.yml` and `docker-compose.test.yml`.
5. Keep dev and test stacks runnable in parallel with repo-derived Compose `name:` values and non-overlapping host ports.

Maintenance cadence:

- review manifests when adding a new stack or archetype
- retire stale examples before adding newer alternates
- update doctrine only for durable rules, not one-off incidents
