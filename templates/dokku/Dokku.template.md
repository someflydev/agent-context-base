# Dokku Deployment Notes

This repo is prepared for Dokku-style single-service deployment.

## Required Files

- `Procfile`
- `app.json`
- `scripts/smoke/deploy_smoke.sh`

## Expected Environment

- app name: `{{repo_slug}}`
- exposed port: `{{app_port}}`
- release command: `{{release_command}}`

## Guardrails

- keep the boot command explicit
- keep release and migration steps explicit
- prove local smoke and integration checks before trusting deploy wiring

