# Ruby Hanami API Endpoint Example

`ShowReport < Hanami::Action` handles the request. `Hanami::Router` registers it with
`get "/api/reports/:tenant_id", to: ShowReport.new`. The action instance is passed
directly — actions are plain objects and can be initialized with dependencies.

**Route registration shape:** `Hanami::Router.new { get "/path/:param", to: ActionClass.new }` —
declarative router block. No macro, no annotation. For dependency injection, override
`initialize` on the action and pass collaborators at `ShowReport.new(repo: ...)`.

**Request parsing:** `request.params[:tenant_id].to_s` — Hanami merges path, query, and
body params into a single `params` hash. `.to_s` ensures a string even if the param is
absent (returns `""`). No limit parameter extraction is shown.

**Service/transport separation:** `ReportsRepo.fetch(tenant_id)` hides the Sequel query
from the action. The action does not call `DB` directly. This is the correct Hanami
pattern — actions delegate to repos, not to raw DB queries.

**Error handling:** `ReportsRepo.fetch` returns a stub hash when no row is found via
the `|| { ... }` fallback, so the action always returns 200. A missing tenant gets stub
data, not 404. Add `halt 404` or `response.status = 404` before the `response.body`
assignment when the repo returns nil in a derived repo.

**Response shape:** `response.format = :json` sets `Content-Type: application/json`.
`response.body = JSON.generate(...)` assembles JSON from a plain Ruby hash via the
standard library. No typed response model — schema is by convention. Consider a
serializer (e.g., `alba`) for larger response shapes when deriving.

Use it with:

- `context/workflows/add-api-endpoint.md`
- `context/stacks/ruby-hanami.md`
- `context/doctrine/testing-philosophy.md`

Related files:

- `examples/canonical-api/ruby-hanami-api-endpoint-example.rb`
- `examples/canonical-api/ruby-hanami-example/app/actions/reports/show.rb`
- `examples/canonical-api/ruby-hanami-example/lib/ruby_hanami_example/persistence.rb`
