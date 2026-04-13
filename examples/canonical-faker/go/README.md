# Go TenantCore Example

This example demonstrates two contrasting Go faker styles for the same
TenantCore relational dataset:
- `gofakeit` as the primary imperative pipeline
- `go-faker/faker` as a struct-tag contrast for atomic field population

Key teaching points:
- Go requires explicit seed management. The `gofakeit` instance and the
  weighted `math/rand` instance use the same seed, but they remain separate
  objects.
- The pool pattern handles relational integrity. Faker libraries do not create
  memberships, projects, or audit-event graph consistency on their own.
- `struct_tag.go` shows that struct tags are useful for leaf fields, but the
  orchestration layer still owns graph correctness.

Quick start:

```bash
go run ./cmd/generate/ -profile smoke
```

Run tests:

```bash
go test ./...
```

Validate generated output:

```bash
python3 ../domain/validate_output.py --input-dir ./output/smoke
```

Honest note: Go's weighted distribution APIs are less ergonomic than Python's
or Chance's helper surface, so `internal/distributions/distributions.go` uses a
manual weighted-slice approach.
