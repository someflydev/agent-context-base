# NATS Jetstream And Meilisearch

Purpose: event flow and lightweight search.

Common change surfaces:

- subjects and consumer configuration
- indexing workers
- search endpoints

Testing:

- publish/consume/index flow against real containers
- isolated streams and indexes in test
