# Tool Invocation Discipline

## The Problem

When an assistant starts a task in a derived repo without pre-established invocation paths, it
bumbles: tries `python`, fails, tries `python3`, fails, tries global `pytest`, fails, installs
tools globally (causing version drift), and retries variations until something sticks. The same
pattern recurs with `templ` in Go repos (`go install` pollutes `$GOPATH/bin` instead of using
`go tool`), with Playwright browsers installed globally rather than locally, and with `npm` used
in Bun projects.

## The Rule

Determine the correct invocation path on the first attempt. Use project-local tools exclusively.
Never probe with multiple fallbacks. Never install tools globally in a project context.

---

## Python / FastAPI / uv

**Runtime assumption:** `uv` is globally available (confirmed by `pyproject.toml` + `uv.lock`
signals). System `python`, `python3`, and `pip` must never be used for project work.

### One-time setup

```bash
uv venv --python 3.12 .venv_tools    # use the version from requires-python; default 3.12
uv pip install --python .venv_tools/bin/python pytest httpx pytest-asyncio
```

To add Playwright:

```bash
uv pip install --python .venv_tools/bin/python pytest-playwright playwright
.venv_tools/bin/playwright install chromium
```

### Invocation

```bash
.venv_tools/bin/pytest tests/unit/
.venv_tools/bin/pytest tests/integration/
.venv_tools/bin/pytest tests/e2e/          # if playwright present
```

### Never

- `python -m pytest` or `python3 -m pytest`
- `pip install pytest` (global install)
- `source .venv_tools/bin/activate` — always use the explicit `.venv_tools/bin/` path, never activate
- Bare `pytest` with no path prefix

### Gitignore

`.venv_tools/` and `.venv/` are in `.gitignore`. Never commit either.

---

## TypeScript / Hono / Bun

**Runtime assumption:** `bun` is globally available (confirmed by `bun.lockb` or `bun.lock`
signal). Never use `npm`, `npx`, or `node` to manage or run a Bun project.

### One-time setup

```bash
bun install
bunx playwright install chromium    # only if the project uses Playwright
```

### Invocation

```bash
bun test                            # Bun's built-in test runner
bun run test:e2e                    # or the project-defined e2e script
bunx playwright test                # direct Playwright invocation
```

### Never

- `npm install` in a Bun repo
- `npx playwright` — use `bunx playwright` instead
- Bare `node` to run Bun-native scripts

### Gitignore

`node_modules/` — Bun creates this for compatibility. Already in the template.

---

## TypeScript / Node (non-Bun stacks)

**Runtime assumption:** Node is available via nvm or system install. Confirm with `node --version`.

### One-time setup

```bash
npm install
npm install --save-dev @playwright/test     # if Playwright needed
./node_modules/.bin/playwright install chromium
```

### Invocation

```bash
./node_modules/.bin/playwright test         # prefer explicit path over global npx
npm test
```

### Never

- Global `playwright install` (outside the project's `node_modules`)
- Bare `playwright` with no path prefix

### Gitignore

`node_modules/`

---

## Go / Echo / templ

**Runtime assumption:** Go toolchain is globally available. **Minimum required version: Go 1.24**
(required for the `-tool` flag approach to project-scoped tool management).

### One-time setup — templ

```bash
go get -tool github.com/a-h/templ/cmd/templ@latest
```

The `-tool` flag records `templ` in `go.mod` as a project-scoped tool dependency, pinned in
`go.sum`. This requires no global install and survives `go mod tidy`.

### Invocation

```bash
go tool templ generate          # generate .go files from .templ sources
go test ./...                   # run all tests
go test ./tests/e2e/...         # run e2e tests only
```

### Playwright (Go)

```bash
go get github.com/playwright-community/playwright-go
go run github.com/playwright-community/playwright-go/cmd/playwright install --with-deps chromium
```

E2e tests live in `tests/e2e/` as `*_test.go` files and run with:

```bash
go test ./tests/e2e/...
```

### Never

- `go install github.com/a-h/templ/cmd/templ` — this writes to `$GOPATH/bin` and causes version drift
- Using Go versions before 1.24 for the `-tool` approach (fall back to explicit `//go:generate` directives if the version is older)

---

## Rust / Axum

**Runtime assumption:** Rust toolchain and `cargo` are globally available via `rustup`. No
separate tool environment is needed.

### Invocation

```bash
cargo test                      # run all tests
cargo run                       # run the application
cargo build --release           # production build
```

### Never

- `cargo install` for project-specific utilities (use `cargo install` only for global dev tools)

---

## Elixir / Phoenix

**Runtime assumption:** Elixir and Mix are available (via asdf or system install). No separate
tool environment is needed.

### One-time setup

```bash
mix deps.get
```

### Invocation

```bash
mix test
mix phx.server
```

---

## Kotlin / http4k / Exposed

**Runtime assumption:** The Gradle wrapper (`gradlew`) is committed to the repo. Use it
exclusively. Never rely on a globally installed Gradle.

### Invocation

```bash
./gradlew test
./gradlew run
```

### Never

- Bare `gradle test` — this bypasses the pinned wrapper version

---

## Scala / Tapir / http4s / ZIO

**Runtime assumption:** `sbt` is globally available.

### Invocation

```bash
sbt test
sbt run
```

---

## Clojure / Kit / next.jdbc

**Runtime assumption:** Clojure CLI tools are globally available.

### Invocation

```bash
clojure -M:test         # test alias — confirm the exact alias name in deps.edn first
clojure -M:run          # run alias — confirm the exact alias name in deps.edn first
```

### Never

- Assuming alias names without checking `deps.edn`

---

## Ruby / Hanami

**Runtime assumption:** Ruby and Bundler are available. All gem execution goes through `bundle exec`.

### One-time setup

```bash
bundle install
```

### Invocation

```bash
bundle exec rspec               # or `bundle exec rake test` depending on project setup
bundle exec hanami server
```

### Never

- `gem install rspec` globally
- Bare `rspec` without `bundle exec`

### Gitignore

`.bundle/` if bundle path is local; `vendor/bundle/` if vendored.

---

## OCaml / Dream / Caqti / Tyxml

**Runtime assumption:** opam switch is configured and `dune` is available within the switch.

### Invocation

```bash
dune build
dune test
```

---

## Crystal / Kemal / Avram

**Runtime assumption:** Crystal and Shards are available.

### One-time setup

```bash
shards install
```

### Invocation

```bash
crystal spec
```

---

## Dart / Dartfrog

**Runtime assumption:** Dart SDK is available.

### One-time setup

```bash
dart pub get
```

### Invocation

```bash
dart test
```

---

## Nim / Jester / HappyX

**Runtime assumption:** Nim and Nimble are available.

### One-time setup

```bash
nimble install
```

### Invocation

```bash
nimble test
```

---

## Zig / Zap / Jetzig

**Runtime assumption:** Zig toolchain is available.

### Invocation

```bash
zig build
zig build test
```

---

## Playwright for Non-TypeScript HTMX Backends

Two patterns are supported for HTMX backends not served from a Node/Bun runtime. Use the one
that matches the backend language.

### Go backend (playwright-go)

`github.com/playwright-community/playwright-go` is the correct choice for Go/Echo/templ repos.
Tests are `.go` files in `tests/e2e/` and run with the standard Go test runner:

```bash
go get github.com/playwright-community/playwright-go
go run github.com/playwright-community/playwright-go/cmd/playwright install --with-deps chromium
go test ./tests/e2e/...
```

See `examples/canonical-integration-tests/playwright-go-htmx-example_test.go` for the structural
pattern (arrange → act → assert, semantic assertions, no pixel checks).

### Python backend (pytest-playwright)

`pytest-playwright` is the correct choice for Python/FastAPI repos. Tests are `.py` files in
`tests/e2e/` and run through the `.venv_tools/bin/pytest` path:

```bash
uv pip install --python .venv_tools/bin/python pytest-playwright playwright
.venv_tools/bin/playwright install chromium
.venv_tools/bin/pytest tests/e2e/
```

See `examples/canonical-integration-tests/playwright-python-htmx-example.py` for the structural
pattern.

### When to use TypeScript Playwright

If the repo is TypeScript/Hono/Bun or the project already has `@playwright/test` in `package.json`,
use the TypeScript examples in `examples/canonical-integration-tests/*.spec.ts`.

---

## This Repo (agent-context-base)

This meta-repo uses its own verification suite that does not follow the derived-repo patterns above.

```bash
python3.14 -m unittest verification.examples.data.test_storage_examples -v
```

Run with `python3.14 -m unittest` and dotted module paths from the repo root. Never use `pytest`
in this repo. This convention is specific to this base repo's verification suite and does **not**
apply to derived repos.
