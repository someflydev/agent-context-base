# Compose Isolation Anchor

- both `docker-compose.yml` and `docker-compose.test.yml` need a top-level `name:`
- dev and test Compose names must differ, and test should end with `-test`
- host ports must be explicit and non-overlapping across dev and test
- dev data stays under `docker/volumes/dev/`
- test data stays under `docker/volumes/test/`
- destructive reset or seed flows must target the test Compose file only
