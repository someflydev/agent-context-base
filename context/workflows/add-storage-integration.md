# Add Storage Integration

Use this workflow when connecting a repo to a database, cache, queue, or search engine.

## Preconditions

- the target storage system is chosen
- Docker-backed dev and test isolation is defined

## Sequence

1. define the boundary and contract clearly
2. add configuration and local Compose wiring
3. implement the smallest real path through the storage layer
4. add smoke coverage if the feature affects a main path
5. add minimal real-infra integration tests against the isolated test stack
6. document seed, reset, and fixture boundaries if applicable

## Outputs

- storage integration
- test-stack verification
- any required seed or operational docs

## Related Docs

- `context/doctrine/compose-port-and-data-isolation.md`
- storage-specific stack docs
- `examples/canonical-storage/README.md`

## Common Pitfalls

- relying only on mocks for the first real storage path
- sharing dev volumes with test runs
- using default host ports that collide with other repos

