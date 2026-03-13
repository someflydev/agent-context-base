import asyncdispatch
import json
import jester
import strformat

proc reportFragment(tenantId: string; totalEvents: int): string =
  fmt"""
<section id="report-card-{tenantId}" class="report-card">
  <header class="report-card__header">Tenant {tenantId}</header>
  <strong class="report-card__value">{totalEvents}</strong>
  <span class="report-card__status">updated just now</span>
</section>
"""

proc chartDataset(metric: string): JsonNode =
  %*{
    "metric": metric,
    "series": [
      {
        "name": metric,
        "points": [
          {"x": "2026-03-01", "y": 18},
          {"x": "2026-03-02", "y": 24},
          {"x": "2026-03-03", "y": 31},
        ],
      }
    ],
  }

routes:
  get "/healthz":
    resp %*{
      "status": "ok",
      "service": "nim-jester-happyx-example",
    }

  get "/api/reports/@tenantId":
    resp %*{
      "tenant_id": @"tenantId",
      "report_id": "daily-signups",
      "total_events": 42,
    }

  get "/fragments/report-card/@tenantId":
    resp reportFragment(@"tenantId", 42)

  get "/data/chart/@metric":
    resp chartDataset(@"metric")

runForever()
