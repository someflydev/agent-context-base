# Dokku-Deployable Web Service

Purpose: define expectations for repos intended to ship as a small web service or API on Dokku.

Load this pack when:

- the task adds `Procfile`, `app.json`, or deploy docs
- env management, release steps, or persistent storage affect deployment
- the repo is a small service where Dokku is the likely target

Expect:

- a simple web process entrypoint
- explicit env var documentation
- clear persistent storage notes
- startup and health smoke coverage

Avoid:

- Traefik-first assumptions
- orchestration-heavy packaging by default
- hidden deploy-time behavior
