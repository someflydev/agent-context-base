# Clojure Kit next.jdbc Hiccup HTML Fragment Example

`report-card-fragment` uses Hiccup2 (`hiccup2.core/html`) to generate the fragment.
The fragment route is a Reitit data structure — same shape as the api-endpoint route,
with the content-type set to `text/html` in the Ring response map.

**HTMX fragment contract:** `{:id (str "report-card-" tenant-id) :hx-swap-oob "true"}`
are in the Hiccup attribute map. The `id` is tenant-scoped. The surrounding page must
contain an element with the matching `id` for the out-of-band swap to apply. Hiccup
attribute keywords are emitted verbatim as HTML attribute names.

**Content-type discipline:** `{"content-type" "text/html; charset=utf-8"}` is set
explicitly in the Ring `:headers` map. Hiccup itself does not set content-type; the
route handler is responsible. Omitting it causes the browser and HTMX to receive no
content-type hint.

**Server-side rendering approach:** Hiccup2 — a Clojure DSL where data structures become
HTML. `[:section {:id ...} [:strong ...] [:span ...]]` is the Hiccup form; `h/html`
renders it. `(str ...)` unwraps the `HiccupString` type to a plain `String` for the
Ring response body.

**Escaping and XSS posture:** `hiccup2.core/html` escapes string content by default.
`(str "Tenant " tenant-id)` inside a Hiccup vector is HTML-entity-encoded before output.
Characters like `<` and `>` in `tenant-id` are safe. This is one of Hiccup2's key
advantages over raw string concatenation for fragment rendering.

Use it with:

- `context/workflows/add-api-endpoint.md`
- `context/stacks/clojure-kit-nextjdbc-hiccup.md`
- `context/doctrine/testing-philosophy.md`

Related files:

- `examples/canonical-api/clojure-kit-nextjdbc-hiccup-html-fragment-example.clj`
- `examples/canonical-api/clojure-kit-nextjdbc-hiccup-example/src/clojure_kit_nextjdbc_hiccup_example/html.clj`
