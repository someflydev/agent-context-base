# Output Profiles

## Profile Definitions

| Profile | Orgs | Users | Memberships | Projects | Audit Events | API Keys | Invitations |
| --- | --- | --- | --- | --- | --- | --- | --- |
| smoke | 3 | 10 | ~18 | ~9 | ~50 | ~5 | ~5 |
| small | 20 | 200 | ~400 | ~100 | ~2,000 | ~50 | ~30 |
| medium | 200 | 5,000 | ~12,000 | ~1,500 | ~50,000 | ~500 | ~200 |
| large | 2,000 | 50,000 | ~150,000 | ~15,000 | ~500,000 | ~5,000 | ~1,500 |

Approximate counts use the documented cardinality distributions, so exact row
totals vary slightly by profile and seed.

## Profile Selection

- `smoke`: CI gate profile. Fast, deterministic, and always seeded with `42`.
- `small`: local development profile with enough data to observe skew and
  relationships.
- `medium`: demo or staging profile for realistic usage and UI load.
- `large`: benchmark or showcase profile; document memory and write-time costs.

## Implementation Notes

- Profiles are additive: larger profiles generate the same entity types and
  rules as smaller profiles, just at higher scale.
- `medium` and `large` should use chunked writes for JSONL and CSV exports to
  avoid avoidable memory spikes during output.
- Every profile must pass the same cross-field validation rules before output.
- The validation report should emit actual row counts rather than pretending
  approximate table targets are exact.
