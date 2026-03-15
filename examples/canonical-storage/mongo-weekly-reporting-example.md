# MongoDB Weekly Reporting Example

Use weekly-bucketed collections for request/response log workloads where retention is managed by dropping
entire collections rather than deleting individual documents.

## Collection Naming

Name collections by year and ISO week so the oldest bucket is always easy to identify and drop:

```text
request_logs_2026_w10
request_logs_2026_w11
request_logs_2026_w12
```

A helper determines the active collection name from the current date:

```python
from datetime import date


def weekly_collection_name(prefix: str = "request_logs", d: date | None = None) -> str:
    d = d or date.today()
    year, week, _ = d.isocalendar()
    return f"{prefix}_{year}_w{week:02d}"
```

## Document Shape

Store a cleaned, bounded shape — not the raw HTTP payload. Unbounded payloads make indexes expensive and
aggregations slow.

```json
{
  "_id": "<ObjectId>",
  "tenant_id": "acme",
  "report_id": "daily-signups",
  "request_at": "2026-03-10T14:22:00Z",
  "response_status": 200,
  "response_ms": 142,
  "payload_version": 2,
  "row_count": 84,
  "error_code": null
}
```

Fields that must always be present:

- `tenant_id` — drives index selectivity
- `report_id` — identifies the report type
- `request_at` — ISO 8601 UTC timestamp
- `response_status` — HTTP status integer
- `payload_version` — bump when document shape changes

Fields that must never be stored in this collection:

- raw request body or response body
- PII fields (email, full name, IP address)

## Index Strategy

Create a compound index on the most common filter path, with a `partialFilterExpression` to skip errored
documents when counting successful reports:

```javascript
db.request_logs_2026_w12.createIndex(
  { tenant_id: 1, report_id: 1, request_at: -1 },
  {
    name: "tenant_report_time_success",
    partialFilterExpression: { response_status: { $lt: 400 } }
  }
)
```

This index only covers successful responses, which is where the reporting queries land. It avoids index
bloat from error documents that would otherwise be indexed but never queried on this path.

Create a separate sparse index for error-rate monitoring queries:

```javascript
db.request_logs_2026_w12.createIndex(
  { tenant_id: 1, error_code: 1 },
  {
    name: "tenant_errors_sparse",
    sparse: true
  }
)
```

## Aggregation Pipeline Examples

### Weekly summary per tenant and report

```javascript
db.request_logs_2026_w12.aggregate([
  {
    $match: {
      tenant_id: "acme",
      response_status: { $lt: 400 }
    }
  },
  {
    $group: {
      _id: {
        report_id: "$report_id",
        day: { $dateTrunc: { date: "$request_at", unit: "day" } }
      },
      request_count: { $sum: 1 },
      avg_response_ms: { $avg: "$response_ms" },
      total_rows: { $sum: "$row_count" }
    }
  },
  {
    $sort: { "_id.day": -1, "request_count": -1 }
  }
])
```

### Error-rate facet across report types

```javascript
db.request_logs_2026_w12.aggregate([
  { $match: { tenant_id: "acme" } },
  {
    $facet: {
      by_status_class: [
        {
          $group: {
            _id: {
              $switch: {
                branches: [
                  { case: { $lt: ["$response_status", 400] }, then: "success" },
                  { case: { $lt: ["$response_status", 500] }, then: "client_error" }
                ],
                default: "server_error"
              }
            },
            count: { $sum: 1 }
          }
        }
      ],
      slowest_reports: [
        { $sort: { response_ms: -1 } },
        { $limit: 5 },
        { $project: { _id: 0, report_id: 1, response_ms: 1, request_at: 1 } }
      ]
    }
  }
])
```

## Retention

Drop the entire collection when it ages past the retention window. Never delete individual documents for
routine retention — dropping is an O(1) metadata operation; document-level deletes scan and fragment the
collection.

```python
def drop_old_weekly_collections(db, prefix: str, keep_weeks: int = 8) -> list[str]:
    """Drop weekly collections older than keep_weeks from today."""
    today = date.today()
    cutoff_year, cutoff_week, _ = today.isocalendar()
    dropped = []
    for name in db.list_collection_names():
        if not name.startswith(prefix + "_"):
            continue
        parts = name.rsplit("_w", 1)
        if len(parts) != 2:
            continue
        try:
            coll_week = int(parts[-1])
        except ValueError:
            continue
        # Simplified: assumes same year. Production use requires full year parsing.
        if coll_week < (cutoff_week - keep_weeks):
            db.drop_collection(name)
            dropped.append(name)
    return dropped
```

This helper is documentation-shaped only. Production use requires full year-boundary handling.

## Verification Level

Structure-verified (file existence and marker checks only). No live MongoDB instance is wired in the
default verification tier.

## When To Use This Example vs. `redis-mongo-shape-example.md`

Use this example when:

- you need a dedicated MongoDB workload without Redis
- the primary design question is collection bucketing, aggregation pipelines, or index strategy

Use `redis-mongo-shape-example.md` when:

- the design combines Redis caching with MongoDB document storage in a single repo
- you need the combined key-prefix and collection-naming convention in one place
