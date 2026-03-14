# Canonical Data Acquisition Examples

Use these examples when a repo needs explicit source research, acquisition, raw retention, parsing, classification, scheduling, and event coordination.

Verification posture:

- doc-level canonical examples only
- intended to pair with the doctrine and workflow files in `context/`
- good fit for `data-acquisition-service` and `multi-source-sync-platform` archetypes

## API Ingestion Source Example

```python
from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
import json

import httpx


@dataclass(frozen=True)
class RawCapture:
    source: str
    fetched_at: datetime
    storage_path: str
    checksum: str
    body: str


class PublicNoticesApiSource:
    source_name = "public_notices_api"

    def __init__(self, client: httpx.Client, archive) -> None:
        self.client = client
        self.archive = archive

    def fetch_window(self, *, updated_after: str | None) -> list[RawCapture]:
        captures: list[RawCapture] = []
        next_url = "https://data.example.gov/v1/notices"
        cursor = updated_after

        while next_url:
            response = self.client.get(next_url, params={"updated_after": cursor}, timeout=30.0)
            response.raise_for_status()
            body = response.text
            fetched_at = datetime.now(UTC)
            checksum = sha256(body.encode("utf-8")).hexdigest()
            storage_path = (
                f"data/raw/{self.source_name}/"
                f"fetched_date={fetched_at:%Y-%m-%d}/"
                f"{checksum}.json"
            )

            self.archive.write_text(
                storage_path,
                body,
                metadata={
                    "source": self.source_name,
                    "fetched_at": fetched_at.isoformat(),
                    "status_code": response.status_code,
                    "cursor": cursor,
                    "content_type": response.headers.get("content-type", "application/json"),
                },
            )

            captures.append(
                RawCapture(
                    source=self.source_name,
                    fetched_at=fetched_at,
                    storage_path=storage_path,
                    checksum=checksum,
                    body=body,
                )
            )

            payload = json.loads(body)
            next_url = payload.get("next")
            cursor = payload.get("last_updated_at", cursor)

        return captures
```

## Scraping Source Example

```python
from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256

import httpx
from bs4 import BeautifulSoup


@dataclass(frozen=True)
class ScrapedDocument:
    listing_url: str
    raw_path: str
    title: str
    posted_on: str


def fetch_procurement_listing(listing_url: str, client: httpx.Client, archive) -> ScrapedDocument:
    response = client.get(listing_url, timeout=30.0)
    response.raise_for_status()

    html = response.text
    fetched_at = datetime.now(UTC)
    checksum = sha256(html.encode("utf-8")).hexdigest()
    raw_path = (
        "data/raw/procurement_portal/"
        f"fetched_date={fetched_at:%Y-%m-%d}/{checksum}.html"
    )
    archive.write_text(
        raw_path,
        html,
        metadata={
            "source": "procurement_portal",
            "url": listing_url,
            "fetched_at": fetched_at.isoformat(),
            "content_type": "text/html",
        },
    )

    soup = BeautifulSoup(html, "html.parser")
    return ScrapedDocument(
        listing_url=listing_url,
        raw_path=raw_path,
        title=soup.select_one("main h1").get_text(strip=True),
        posted_on=soup.select_one("[data-posted-on]").get("data-posted-on", ""),
    )
```

## Raw Download Archival Layout

```text
data/
  raw/
    public_notices_api/
      fetched_date=2026-03-14/
        0d9b...a1.json
        0d9b...a1.meta.json
    procurement_portal/
      fetched_date=2026-03-14/
        7bc2...4f.html
        7bc2...4f.meta.json
  normalized/
    notices/
      run_date=2026-03-14/
        notices.parquet
  state/
    source_checkpoints.json
```

Rules:

- raw body and metadata stay adjacent
- normalized outputs never replace raw captures
- checkpoint state stays outside the raw archive

## Parser And Normalizer Example

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class NormalizedNotice:
    external_id: str
    title: str
    notice_type: str
    published_at: str
    canonical_url: str
    source_name: str
    raw_path: str


def normalize_notice(record: dict[str, Any], *, source_name: str, raw_path: str) -> NormalizedNotice:
    return NormalizedNotice(
        external_id=str(record["id"]).strip(),
        title=str(record["title"]).strip(),
        notice_type=str(record.get("category") or "unknown").strip().lower(),
        published_at=str(record.get("published_at") or ""),
        canonical_url=str(record.get("url") or ""),
        source_name=source_name,
        raw_path=raw_path,
    )
```

## Classification Example

```python
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ClassificationDecision:
    category: str
    confidence: float
    classifier_version: str
    rationale: str


def classify_notice(title: str, notice_type: str) -> ClassificationDecision:
    title_lower = title.lower()
    if "road" in title_lower or "bridge" in title_lower:
        return ClassificationDecision(
            category="transportation",
            confidence=0.92,
            classifier_version="rules-2026-03-14",
            rationale="matched transportation infrastructure keywords",
        )
    if notice_type == "housing":
        return ClassificationDecision(
            category="housing",
            confidence=0.88,
            classifier_version="rules-2026-03-14",
            rationale="source category normalized to housing",
        )
    return ClassificationDecision(
        category="general",
        confidence=0.55,
        classifier_version="rules-2026-03-14",
        rationale="fell back to default category",
    )
```

## Recurring Sync Configuration Example

```yaml
sync_jobs:
  - name: public_notices_api
    cron: "0 6,18 * * *"
    timezone: America/Chicago
    emits_event: source.sync.requested
    payload:
      source: public_notices_api
      mode: incremental
      lookback_hours: 18
    concurrency_key: source:public_notices_api
    timeout_seconds: 1800
  - name: procurement_portal
    cron: "30 6,18 * * *"
    timezone: America/Chicago
    emits_event: source.sync.requested
    payload:
      source: procurement_portal
      mode: incremental
      listing_limit: 25
    concurrency_key: source:procurement_portal
    timeout_seconds: 2400
```

## Backoff And Retry Configuration Example

```yaml
sources:
  public_notices_api:
    rate_limit:
      requests_per_minute: 30
      burst: 5
    retry:
      retryable_statuses: [408, 429, 500, 502, 503, 504]
      max_attempts: 5
      backoff: exponential_jitter
      initial_delay_ms: 500
      max_delay_ms: 30000
  procurement_portal:
    rate_limit:
      requests_per_minute: 10
      burst: 2
    retry:
      retryable_statuses: [429, 503]
      max_attempts: 4
      backoff: exponential_jitter
      initial_delay_ms: 1500
      max_delay_ms: 60000
```

## Event-Streaming Sync Example

```json
{
  "stream": "source-sync",
  "subjects": [
    "source.sync.requested",
    "source.fetch.completed",
    "source.normalize.completed",
    "source.classify.completed",
    "source.sync.failed"
  ],
  "events": {
    "source.sync.requested": {
      "producer": "scheduler",
      "payload_keys": ["source", "run_id", "sync_mode", "window_start", "window_end"],
      "idempotency_key": "source:run_id"
    },
    "source.fetch.completed": {
      "producer": "source-adapter",
      "payload_keys": ["source", "run_id", "raw_path", "cursor", "record_count"],
      "idempotency_key": "raw_path"
    },
    "source.sync.failed": {
      "producer": "fetcher-or-consumer",
      "payload_keys": ["source", "run_id", "stage", "error_class", "retryable"],
      "idempotency_key": "source:run_id:stage"
    }
  }
}
```
