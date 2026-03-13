# Crystal Kemal Avram Scenario Harness

Docker-backed smoke verification for the Crystal Kemal plus Avram runtime bundle.

Checks:

- Docker image builds from `examples/canonical-api/crystal-kemal-avram-example`
- container boots and answers `/healthz`
- JSON API route returns a stable report envelope
- HTML fragment route returns HTMX-friendly markup
- chart dataset route returns visualization-ready JSON
