## Multi-Backend Architecture

Service seams must be versioned and documented. Each backend should own a clearly named contract, runtime, and storage responsibility.

Prefer explicit REST, gRPC, or event boundaries over ad hoc shared-database coupling unless the repo is intentionally exploring that as a controlled experiment.
