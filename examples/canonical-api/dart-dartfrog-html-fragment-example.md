# Dart Dart Frog HTML Fragment Example

`renderReportCard` builds the fragment as a Dart triple-quoted multiline string with
`$tenantId` and `$totalEvents` interpolation. The `onRequest` handler sets an explicit
content-type header and passes the rendered string as the body.

**HTMX fragment contract:** `id="report-card-$tenantId"` and `hx-swap-oob="true"` are
present in the multiline string. The `id` is tenant-scoped. The surrounding page must
contain an element with the matching `id` for the out-of-band swap to apply.

**Content-type discipline:** `headers: const {'content-type': 'text/html; charset=utf-8'}`
is set explicitly on the `Response` constructor. Dart Frog does not infer content-type
from a string body; omitting it may cause HTMX or the browser to treat the response as
`text/plain`.

**Server-side rendering approach:** Dart triple-quoted string literal (`'''...'''`) with
`$tenantId` and `$totalEvents` interpolation. No template engine or HTML builder.
`renderReportCard` is a standalone named function returning a `String`.

**Escaping and XSS posture:** Dart string interpolation does not HTML-escape values.
`$tenantId` is inserted raw into the markup. If `tenantId` can contain `<`, `>`, or `&`,
use `HtmlEscape().convert(tenantId)` from `dart:convert` when deriving. `$totalEvents`
is an `int` — safe.

Use it with:

- `context/workflows/add-api-endpoint.md`
- `context/stacks/dart-dartfrog.md`
- `context/doctrine/testing-philosophy.md`

Related files:

- `examples/canonical-api/dart-dartfrog-html-fragment-example.dart`
- `examples/canonical-api/dart-dartfrog-example/routes/index.dart`
