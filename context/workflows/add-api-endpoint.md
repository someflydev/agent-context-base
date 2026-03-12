# Add API Endpoint

Use this workflow when adding a new HTTP route, handler, or controller action.

## Preconditions

- the active web stack is known
- request and response shape are clear enough to implement

## Sequence

1. identify router, handler, validation, service, and persistence touch points
2. follow the canonical route shape for the stack
3. implement the happy path first
4. add smoke coverage for one representative request
5. add minimal real-infra integration tests if the endpoint writes or reads through real storage, queues, or search systems
6. update docs or manifests if the endpoint changes repo signals materially

## Outputs

- route implementation
- smoke test
- integration coverage when boundary changes require it

## Related Docs

- stack doc for the active web framework
- `examples/canonical-api/README.md`

## Common Pitfalls

- putting business logic directly in transport handlers
- treating a storage-backed endpoint as smoke-test-only work
- copying route structure from the wrong stack example

