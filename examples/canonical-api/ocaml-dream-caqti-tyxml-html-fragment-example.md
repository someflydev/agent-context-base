# OCaml Dream Caqti TyXML HTML Fragment Example

`render_report_card` builds the fragment using TyXML (`Tyxml.Html`) combinators. `Dream.html`
sets the content-type automatically. The fragment handler is curried with a `report_lookup`
function injected at startup — the same partial-application pattern as the api-endpoint.

**HTMX fragment contract:** `a_id ("report-card-" ^ tenant_id)` and
`Unsafe.string_attrib "hx-swap-oob" "true"` are in the TyXML attribute list. The `id`
is tenant-scoped. `Unsafe.string_attrib` is required because TyXML does not have a
typed attribute for HTMX extensions — this is the correct idiom for adding non-standard
HTML attributes in TyXML.

**Content-type discipline:** `Dream.html` sets `Content-Type: text/html` automatically.
No explicit header setting is needed in Dream's HTML response path.

**Server-side rendering approach:** TyXML (`Tyxml.Html`) — a typed OCaml library for
HTML generation using combinators (`section`, `strong`, `span`, `p`, `txt`). TyXML
validates the HTML tree structure at **compile time**: placing a block element inside
an inline element is a type error. `Format.asprintf "%a" (Tyxml.Html.pp_elt ())` serializes
the element to a string.

**Escaping and XSS posture:** `txt ("Tenant " ^ tenant_id)` creates a text node that
TyXML HTML-escapes automatically. `tenant_id` cannot inject markup through a `txt` node.
The `"true"` value in `Unsafe.string_attrib "hx-swap-oob" "true"` is a literal — not
user-controlled — so there is no injection risk there.

Use it with:

- `context/workflows/add-api-endpoint.md`
- `context/stacks/ocaml-dream-caqti-tyxml.md`
- `context/doctrine/testing-philosophy.md`

Related files:

- `examples/canonical-api/ocaml-dream-caqti-tyxml-html-fragment-example.ml`
- `examples/canonical-api/ocaml-dream-caqti-tyxml-example/bin/main.ml`
