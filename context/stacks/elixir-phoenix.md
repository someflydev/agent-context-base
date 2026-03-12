# Elixir Phoenix

Purpose: Elixir-first service stack for interactive or API-heavy systems.

Typical paths:

- `lib/..._web/`
- `lib/.../`
- `test/`

Conventions:

- keep context boundaries clear
- place controller/live/plug logic in the appropriate Phoenix layer

Testing:

- mix tests
- real infra tests when external stores or queues matter
