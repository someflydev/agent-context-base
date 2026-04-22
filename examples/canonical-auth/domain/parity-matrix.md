# Canonical Auth Parity Matrix

Status legend: [ ] not started · [~] partial · [x] complete

| Language | JWT middleware | Request-scoped auth context | Route metadata registry | All 14 routes | /me JSON | /me allowed_routes | Super-admin flow | Tenant-admin flows | Tenant-member flow | Cross-tenant denial | Stale acl_ver test | Smoke tests passing | README.md |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Python | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] |
| TypeScript | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [~] | [x] |
| Go | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] |
| Rust | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] |
| Java | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] |
| Kotlin | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] |
| Ruby | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [~] | [~] | [x] |
| Elixir | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] |

Update each row only after that language implementation passes the shared smoke
and unit-test contract.

* [~] TypeScript smoke tests passing: Tests are fully implemented but could not be executed locally because the bun runtime is not available.
* [~] Ruby stale `acl_ver` and smoke tests passing: The Ruby example is implemented and Ruby syntax-checked, but `bundle exec rspec` could not run locally because the host Ruby is `2.6.10` while the example targets a newer Hanami-capable toolchain.
