# Synthetic Dataset Design Skill

## When to Use

Use this skill when asked to generate seed data, fixtures, synthetic datasets,
or realistic test data that spans multiple related entities.

## The Seven-Step Generation Pipeline

### Step 1: Define the entity graph and generation order

Draw the dependency graph and write it down in the example README before coding.
Identify which entities are roots and which are leaves.

### Step 2: Choose a seed and make it explicit

Pick a seed such as `42` and use it consistently across the whole pipeline.
Every random decision must flow from the same seeded generator.

### Step 3: Generate roots first, build ID pools

Generate all root entities and store their IDs in a lookup structure. Do not
move to dependent entities until the root pool is complete.

### Step 4: Generate each dependent layer in order

For each layer, sample from the parent pool, generate children, and apply the
documented cardinality and weighted distribution rules.

### Step 5: Apply cross-field consistency rules

After generation, check linked constraints explicitly.
- membership `user_id` must exist in the users pool
- event `user_id` must be a member of event `org_id`
- event `project_id` must belong to event `org_id`

### Step 6: Validate

Run a validation pass for FK integrity, uniqueness, row counts, temporal
ordering, and distribution sanity. Produce a human-readable validation report
and stop if validation fails.

### Step 7: Write output

Write JSONL, CSV, or SQL for the requested profile size. Use chunked writes for
medium and large profiles, and report final row counts.

## Common Design Mistakes

- Generating children before parents, which guarantees broken references.
- Mixing seeded and unseeded randomness, which destroys replayability.
- Using uniform random counts where the domain should be skewed.
- Writing output before validation, which turns bad data into a committed artifact.
- Treating faker providers as business-rule enforcement instead of value sources.
