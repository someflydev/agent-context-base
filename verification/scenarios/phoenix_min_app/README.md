# phoenix_min_app

Smoke harness for `examples/canonical-api/phoenix-example/`. The native check runs `mix deps.get` and `mix compile` against the project directory to confirm the dependency graph resolves and all modules compile without errors. The Docker check builds the image from the project's `Dockerfile`, starts a container bound to a free local port, polls `GET /healthz` until the server is ready (up to 35 seconds), asserts HTTP 200 and `{"status": "ok"}` in the response body, then removes the container.
