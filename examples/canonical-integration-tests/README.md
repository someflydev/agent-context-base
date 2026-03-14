# Canonical Integration Test Examples

Use this category when the change crosses a real storage or service boundary and smoke tests alone would be misleading.

Strong examples in this category should show:

- `docker-compose.test.yml` as the only target for reset and fixture flows
- explicit boot and teardown of the test stack
- a real write and a real read or query assertion
- small deterministic fixture data
- Playwright assertions that prove backend-driven UI semantics when the interface depends on HTMX fragments or chart payloads

Choose this category after the route or command shape is already clear from a stack-specific example.
