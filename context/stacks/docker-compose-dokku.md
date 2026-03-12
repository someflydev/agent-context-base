# Docker Compose And Dokku

Purpose: local orchestration and simple deployment alignment.

Rules:

- keep filenames `docker-compose.yml` and `docker-compose.test.yml`
- set top-level `name:` to repo slug and repo slug plus `-test`
- use explicit non-default host ports
- reserve a separate test port band
- keep test env files and volumes separate

Prevents:

- collisions
- default-port ambiguity
- shared dev/test data
