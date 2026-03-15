# MinIO

Use this pack when a repo uses MinIO as an S3-compatible object store for local development, CI pipelines, or self-hosted environments where data must not leave a network boundary. MinIO is not a managed AWS S3 replacement — deployment decisions about whether to run MinIO in production are outside the scope of this repository.

## When MinIO Is the Right Choice

- **Local dev and CI**: S3 credentials are unavailable, undesirable, or would incur cost. MinIO provides a real object store API without mocking.
- **Self-hosted**: data must remain within a network boundary (compliance, latency, or cost).
- **Integration tests**: tests that need actual multipart upload, presigned URL generation, or bucket lifecycle behavior that S3 mocks do not faithfully reproduce.

Poor fit: repos that need AWS-native features (SQS event notifications, S3 Select, Lambda triggers on upload). MinIO supports many S3 API operations but not every AWS-native extension.

## Typical Repo Surface

- `app/storage/minio.py` or equivalent — client setup with environment variable credentials
- `docker-compose.yml` — `minio/minio` service with named volumes for dev data
- `docker-compose.test.yml` — `minio/minio` service with separate named volume for test data
- `scripts/create_buckets.py` or `minio/mc` startup script — bucket creation on first boot
- `tests/integration/test_minio_*.py` — write/read/presigned-URL integration tests

## Bucket Naming Discipline

- Use a consistent environment prefix: `dev-`, `test-`, `prod-`.
- Keep bucket names lowercase and hyphen-separated. No underscores (S3-compatible clients normalise underscores inconsistently).
- One bucket per major data domain, not one bucket per tenant. Tenant isolation lives in the object key path, not the bucket name.

Examples:
```
dev-report-data
test-report-data
dev-raw-archive
test-raw-archive
```

## Object Key Conventions

Use a deterministic, hierarchical key schema. Predictable keys enable glob-style listing and partition discovery by read layers (DuckDB, Polars, Trino).

```
<domain>/<partition-key>/<date>/<uuid-or-sequence>.parquet
```

Example:
```
reports/tenant_id=acme/date=2026-03-10/part-0001.snappy.parquet
reports/tenant_id=globex/date=2026-03-10/part-0001.snappy.parquet
```

Avoid keys that sort into a hot partition: a pure timestamp prefix concentrates all writes in one shard. Use a domain prefix before the timestamp, or shard by hash prefix when throughput demands it.

## Credentials and Access

Always use environment variables. Never hardcode credentials in application code or commit them.

```
MINIO_ACCESS_KEY=<access-key>
MINIO_SECRET_KEY=<secret-key>
MINIO_ENDPOINT=http://localhost:9000
```

For integration tests, use a fixed test credential pair defined in `docker-compose.test.yml`. Keep test credentials separate from dev credentials so test bucket operations cannot affect dev data.

## Docker Dev Setup

```yaml
services:
  minio:
    image: minio/minio
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: dev-access-key
      MINIO_ROOT_PASSWORD: dev-secret-key
    ports:
      - "9000:9000"   # S3 API
      - "9001:9001"   # Console UI
    volumes:
      - minio-dev-data:/data

volumes:
  minio-dev-data:
```

Bucket creation on startup: use the `minio/mc` (MinIO Client) sidecar image or a one-shot Python script that runs `boto3.create_bucket()` against the local endpoint before tests start. Do not assume buckets exist.

## Presigned URLs

Generate presigned GET URLs for short-lived file access when the download should be delegated to the caller:

```python
url = s3_client.generate_presigned_url(
    "get_object",
    Params={"Bucket": "dev-report-data", "Key": key},
    ExpiresIn=300,  # 5 minutes
)
```

Do not expose bucket credentials to frontend clients. Generate presigned URLs server-side and return only the URL.

## Change Surfaces To Watch

- **Bucket existence**: the boto3 SDK raises `NoSuchBucket` on write if the bucket does not exist. Always create buckets in dev and test startup scripts; do not assume they persist.
- **Path-style vs virtual-hosted-style**: MinIO defaults to path-style (`http://endpoint/bucket/key`). AWS S3 defaults to virtual-hosted-style (`http://bucket.endpoint/key`). Use path-style for MinIO to avoid DNS resolution issues in local environments.
- **Silent key overwrite**: MinIO is an object store, not an append log. Putting an object to an existing key silently overwrites the previous version unless versioning is enabled. Never assume a second write appends.
- **Credential rotation**: dev and test credentials live in docker-compose files, not in application config. Keep them consistent with the env vars the application reads.

## Testing Expectations

- Use a dedicated test bucket (e.g. `test-report-data`) with a fixed test credential pair. Never share dev and test buckets.
- Create the test bucket in test setup; drop or purge it in teardown.
- Prove one write, one existence check, and one read in the integration test.
- If presigned URLs are tested, assert the URL is reachable from the test network (MinIO container must be accessible on the presigned URL host).

## Common Assistant Mistakes

- Not creating buckets before the first write (the SDK will fail with a bucket-not-found error rather than auto-creating).
- Using virtual-hosted-style URL addressing for MinIO instead of path-style.
- Treating MinIO as an append log — keys overwrite silently.
- Sharing dev and test volumes (use separate named Docker volumes for each environment).
- Hardcoding credentials instead of reading from environment variables.
