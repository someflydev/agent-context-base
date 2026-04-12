# Rust - garde (Lane A: Richer Validation DSL)

## Lane
Lane A: derive-based validation, richer than `validator`.

## What garde Does Differently from validator
- `inner()` expresses per-element rules in collections without a separate helper.
- `pattern()` keeps regexes inline instead of forcing a shared `Lazy<Regex>`.
- Cross-field checks can be layered alongside derive rules without overloading
  the field attributes themselves.
- Custom error messages and rule composition are more ergonomic than plain
  `validator` custom hooks.
- Validation context can be threaded through the call site when a rule needs
  extra state beyond the field being checked.

## When to Choose garde over validator
Choose `garde` when you want a richer validation DSL, stronger collection
validation ergonomics, or cleaner custom-rule composition. `validator` remains
the more common ecosystem default, but `garde` is often more pleasant once the
rules move beyond simple field annotations.

## Still Three Separate Libraries
`serde` still owns deserialization, `garde` owns runtime constraints, and
`schemars` owns schema export. This example does not collapse those concerns
into one library.
