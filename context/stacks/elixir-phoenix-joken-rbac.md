# Elixir: Phoenix + Joken + RBAC

## Identity

- Name: `elixir-phoenix-joken-rbac`
- Language: Elixir
- Framework: Phoenix
- Auth library: `Joken`
- Aliases: `phoenix-jwt-rbac`, `elixir-auth-api`, `phoenix-joken`

## Preferred JWT Library

`Joken` is preferred because it is Elixir-native, Plug-friendly, and easy to
compose into a Phoenix pipeline. It provides a clear claim-validation surface
without forcing a lower-level JOSE-first API on the teaching path. `JOSE`
remains the adjacent alternative when lower-level primitives are needed, but it
is not the default because the canonical examples optimize for direct Phoenix
integration.

## Core Dependencies

- `phoenix` — router, controller, and Plug pipeline
- `joken` — token config and verification
- standard Elixir structs or maps — auth context and route metadata
- `plug` testing helpers — request-level verification
- optional HEEx or HTMX fragment helpers — HTML `/me` variant

## Auth Architecture

This stack extends `context/stacks/elixir-phoenix.md` and uses a Plug to
validate the bearer token before protected controllers run. The Plug builds an
auth context and stores it in `conn.assigns`. Controllers and policy helpers
then read route metadata, enforce the required permission, and apply tenant
boundaries without relying on LiveView.

## Token Validation Pattern

```elixir
with {:ok, claims} <- Token.verify_and_validate(token),
     :ok <- ACLVersion.assert_current(claims),
     auth <- AuthContext.from_claims(claims) do
  assign(conn, :auth, auth)
else
  _ -> conn |> put_status(:unauthorized) |> halt()
end
```

## Request Context Pattern

Store validated auth state in `conn.assigns.auth` inside the Plug pipeline.
Keep it request-scoped and pass it to domain services as needed. Avoid process
dictionary or application env shortcuts for current auth state.

## Route Metadata Pattern

Use a module attribute list or dedicated registry module describing method,
path, permission, tenant scope, and docs section. Controllers and `/me`
filtering should query the same registry.

## /me Handler Pattern

The `/me` controller action returns JSON built from token claims, live tenant
and group state, and the filtered route registry. An HTML fragment variant is
optional and should share the same data shape for HTMX-oriented UIs.

## Testing Approach

Use Phoenix request tests with crafted tokens to verify invalid claim rejection,
permission denial, tenant mismatch denial, and `/me` route visibility.

## Canonical Example Path

`examples/canonical-auth/elixir/`

## Known Constraints or Tradeoffs

- Plug pipelines are explicit and reliable, but route metadata lookups should stay centralized
- `Joken` keeps claims cleanly configurable, though some teams may prefer lower-level JOSE access
- this stack is Phoenix controller plus HTMX oriented, not LiveView oriented
