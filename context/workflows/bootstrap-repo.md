# Bootstrap Repo

Purpose: initialize a new repo from this base.

Sequence:

1. set repo slug and update `manifests/repo.profile.yaml`
2. select archetype packs
3. select stack packs
4. prune irrelevant packs if the repo is intentionally narrow
5. add at least one preferred canonical example per common task
6. wire smoke tests and infra rules if containers exist

Pitfalls:

- copying every pack into every repo
- leaving repo profile generic
