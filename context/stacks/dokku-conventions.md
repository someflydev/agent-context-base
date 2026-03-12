# Dokku Conventions

Use this pack when a repo is intended to deploy as a Dokku-managed service.

## Typical Repo Surface

- `Dockerfile` or buildpack config
- `Procfile` where relevant
- release or migration commands
- environment variable docs
- smoke tests that can verify boot success

## Change Surfaces To Watch

- boot command
- runtime environment wiring
- backing-service add-ons
- migration and release hooks

## Testing Expectations

- local smoke tests should prove the app can boot
- if the service depends on a database, queue, or search engine, local integration tests should prove that boundary before deployment is trusted

## Common Assistant Mistakes

- assuming Dokku removes the need for local Docker-backed testing
- hiding release steps in undocumented hooks
- designing one repo as a multi-service platform deployment

