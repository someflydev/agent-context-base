# Zig Jetzig HTML Fragment Example

This example shows the Zig stack posture for HTMX-style HTML fragments:

- let Jetzig own the view surface
- keep the fragment template explicit and small
- render a reusable partial instead of assembling large HTML strings inline

Use it with:

- `context/workflows/add-api-endpoint.md`
- `context/stacks/zig-zap-jetzig.md`
- `context/doctrine/testing-philosophy.md`

Related files:

- `examples/canonical-api/zig-jetzig-html-fragment-example.zig`
- `examples/canonical-api/zig-jetzig-html-fragment-template-example.zmpl`
- `examples/canonical-api/zig-zap-jetzig-example/main.zig`
