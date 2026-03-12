# Repo Bootstrap Checklist

Use this checklist when copying this base repo into a new project.

- Set repo slug and update `manifests/repo.profile.yaml`.
- Select one or more archetype manifests.
- Select only the active stack packs.
- Delete irrelevant stacks and examples if the new repo is intentionally narrow.
- Keep `AGENT.md` and `CLAUDE.md` as routers.
- Create or adapt canonical examples for the most common change surfaces.
- If Docker-backed infra exists, define:
  - `docker-compose.yml`
  - `docker-compose.test.yml`
  - repo-derived Compose `name:` values
  - non-default dev and test host-port bands
  - isolated test env files, volumes, fixtures, and seed/reset flows
- Add smoke tests and minimal real-infra integration tests for significant persistence or cross-service behavior.
