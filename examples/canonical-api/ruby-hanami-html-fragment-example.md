# Ruby Hanami HTML Fragment Example

`ShowReportCard < Hanami::Action` delegates rendering to `ReportCardView < Hanami::View`.
The view is configured with a template path and `config.layout = false` — the layout
suppression is required for fragment responses; without it, Hanami wraps the output in
the root layout.

**HTMX fragment contract:** The `id` and `hx-swap-oob="true"` attributes must be in the
ERB template (`templates/report_cards/show`), not in this Ruby file. The companion `.rb`
wires the action to the view and exposes `tenant_id` and `snapshot` to the template.
Confirm the template contains `id="report-card-<%= tenant_id %>"` and `hx-swap-oob="true"`
before using in an HTMX context.

**Content-type discipline:** `response.format = :html` — Hanami sets
`Content-Type: text/html; charset=utf-8` from the format symbol. This is the Hanami 2
idiom for setting content-type on the response.

**Server-side rendering approach:** `Hanami::View` with an ERB template. `config.template = "report_cards/show"`
points to the template file. `expose :tenant_id` and `expose :snapshot` declare which
variables the template receives. `config.layout = false` disables layout wrapping.
`ReportCardView.new.call(...).to_s` renders the template to a string.

**Escaping and XSS posture:** ERB escapes interpolated values by default in Hanami 2
(`<%= %>` escapes; `<%== %>` is raw). If the template uses `<%= tenant_id %>`, it is safe.
Use `<%== %>` only for pre-sanitized HTML you control.

Use it with:

- `context/workflows/add-api-endpoint.md`
- `context/stacks/ruby-hanami.md`
- `context/doctrine/testing-philosophy.md`

Related files:

- `examples/canonical-api/ruby-hanami-html-fragment-example.rb`
- `examples/canonical-api/ruby-hanami-example/app/actions/report_cards/show.rb`
- `examples/canonical-api/ruby-hanami-example/app/views/report_cards/show.rb`
