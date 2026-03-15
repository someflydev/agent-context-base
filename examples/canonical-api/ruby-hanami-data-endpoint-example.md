# Ruby Hanami Data Endpoint Example

`ShowChart < Hanami::Action` delegates data retrieval to `MetricsRepo.series_for(metric)`,
which hides the Sequel query. The action assembles the chart hash and encodes it with
`JSON.generate` from Ruby's standard library.

**Chart payload contract:** `JSON.generate(metric: metric, series: [{name: metric, points: MetricsRepo.series_for(metric)}])` —
a Ruby hash where `series_for` returns `[{x: bucket_day, y: total}]`. Matches the
`{metric, series: [{name, points: [{x, y}]}]}` chart contract. No typed model; shape
is by hash key convention.

**Typed response encoding:** `JSON.generate` from Ruby's standard library. Symbol keys
(`metric:`, `series:`) serialize as string keys. Any Ruby-serializable value in the hash
is encoded. Schema drift is silent at runtime — no codecs or derive macros to catch it.

**Storage query integration:** `MetricsRepo.series_for(metric)` runs
`DB[:metric_points].where(metric: metric).order(:bucket_day).all` via Sequel. Sequel's
`where(metric: metric)` uses parameterized queries — safe from SQL injection. The
`unless rows.empty?` guard falls back to hardcoded stub points. Replace the stub with
an empty array or raise 404 when deriving.

**Metric parameter safety:** `metric` is `request.params[:metric].to_s`. It flows into
`MetricsRepo.series_for` where Sequel uses it as a parameterized value — safe. It is
also echoed into the response as `metric:` and `name:`. No sanitization shown; normalize
if your frontend treats the metric name as a storage or display key.

Use it with:

- `context/workflows/add-api-endpoint.md`
- `context/stacks/ruby-hanami.md`
- `context/doctrine/testing-philosophy.md`

Related files:

- `examples/canonical-api/ruby-hanami-data-endpoint-example.rb`
- `examples/canonical-api/ruby-hanami-example/app/actions/charts/show.rb`
- `examples/canonical-api/ruby-hanami-example/lib/ruby_hanami_example/persistence.rb`
