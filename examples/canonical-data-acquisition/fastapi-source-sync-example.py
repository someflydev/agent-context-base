from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any, Protocol
from urllib import error, parse, request

import orjson
import polars as pl
from fastapi import APIRouter, Depends, HTTPException


SOURCE_NAME = "github-releases"
ADAPTER_VERSION = "github-releases-v1"

router = APIRouter(prefix="/source-sync", tags=["canonical-data-acquisition"])


@dataclass(slots=True)
class SyncCursor:
    owner: str
    repo: str
    page: int = 1
    etag: str | None = None
    max_attempts: int = 2

    @property
    def checkpoint_token(self) -> str:
        return self.etag or f"page={self.page}"


@dataclass(slots=True)
class FetchResult:
    body: bytes
    fetched_at: datetime
    status_code: int
    content_type: str
    request_url: str
    checkpoint_token: str
    next_page: int | None


@dataclass(slots=True)
class RawCapture:
    source_name: str
    owner: str
    repo: str
    fetched_at: str
    raw_path: str
    metadata_path: str
    sha256: str
    checkpoint_token: str
    request_url: str


@dataclass(slots=True)
class ReleaseProvenance:
    source_name: str
    raw_path: str
    fetched_at: str
    sha256: str
    checkpoint_token: str
    adapter_version: str


@dataclass(slots=True)
class NormalizedReleaseRecord:
    canonical_id: str
    source_id: int
    owner: str
    repo: str
    external_slug: str
    title: str
    published_at: str
    canonical_url: str
    provenance: ReleaseProvenance


@dataclass(slots=True)
class SyncResult:
    raw_capture: RawCapture
    records: list[NormalizedReleaseRecord]
    next_cursor: SyncCursor | None


@dataclass(slots=True)
class SyncReceipt:
    source_name: str
    raw_path: str
    normalized_count: int
    checkpoint_token: str
    next_page: int | None


class RetryableFetchError(RuntimeError):
    """Raised when a sync should retry instead of dropping the cursor."""


class SourceAdapter(Protocol):
    def fetch_release_page(self, cursor: SyncCursor) -> FetchResult:
        """Fetch one raw page without normalizing it."""


class GitHubReleaseAdapter:
    def fetch_release_page(self, cursor: SyncCursor) -> FetchResult:
        query = parse.urlencode({"per_page": 50, "page": cursor.page})
        request_url = f"https://api.github.com/repos/{cursor.owner}/{cursor.repo}/releases?{query}"
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "agent-context-base-canonical-example",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if cursor.etag:
            headers["If-None-Match"] = cursor.etag

        github_request = request.Request(request_url, headers=headers)
        try:
            with request.urlopen(github_request, timeout=20.0) as response:
                body = response.read()
                etag = response.headers.get("ETag")
                return FetchResult(
                    body=body,
                    fetched_at=datetime.now(tz=timezone.utc),
                    status_code=response.status,
                    content_type=response.headers.get("Content-Type", "application/json"),
                    request_url=request_url,
                    checkpoint_token=etag or cursor.checkpoint_token,
                    next_page=cursor.page + 1 if body.strip() else None,
                )
        except error.HTTPError as exc:
            if exc.code in {429, 500, 502, 503, 504}:
                raise RetryableFetchError(f"retryable GitHub failure: {exc.code}") from exc
            raise
        except error.URLError as exc:
            raise RetryableFetchError("transient upstream network failure") from exc


def archive_raw_capture(
    archive_root: Path,
    cursor: SyncCursor,
    fetch_result: FetchResult,
) -> RawCapture:
    fetch_stamp = fetch_result.fetched_at.strftime("%Y/%m/%d/%H%M%SZ")
    capture_dir = archive_root / SOURCE_NAME / cursor.owner / cursor.repo / fetch_stamp
    capture_dir.mkdir(parents=True, exist_ok=True)

    raw_path = capture_dir / f"page-{cursor.page}.json"
    metadata_path = capture_dir / f"page-{cursor.page}.metadata.json"
    raw_path.write_bytes(fetch_result.body)

    checksum = sha256(fetch_result.body).hexdigest()
    capture = RawCapture(
        source_name=SOURCE_NAME,
        owner=cursor.owner,
        repo=cursor.repo,
        fetched_at=fetch_result.fetched_at.isoformat(),
        raw_path=raw_path.as_posix(),
        metadata_path=metadata_path.as_posix(),
        sha256=checksum,
        checkpoint_token=fetch_result.checkpoint_token,
        request_url=fetch_result.request_url,
    )
    metadata_path.write_bytes(orjson.dumps(asdict(capture)))
    return capture


def parse_archived_release_payload(raw_capture: RawCapture) -> list[dict[str, Any]]:
    payload = orjson.loads(Path(raw_capture.raw_path).read_bytes())
    if not isinstance(payload, list):
        raise ValueError("GitHub releases payload must be a JSON array")
    return [item for item in payload if isinstance(item, dict)]


def normalize_release_records(
    raw_capture: RawCapture,
    payload: list[dict[str, Any]],
) -> list[NormalizedReleaseRecord]:
    rows: list[dict[str, Any]] = []
    for item in payload:
        if item.get("draft"):
            continue
        title = str(item.get("name") or item.get("tag_name") or "untitled-release")
        rows.append(
            {
                "canonical_id": f"{SOURCE_NAME}:{raw_capture.owner}/{raw_capture.repo}:{item['id']}",
                "source_id": int(item["id"]),
                "owner": raw_capture.owner,
                "repo": raw_capture.repo,
                "external_slug": str(item.get("tag_name") or ""),
                "title": title,
                "published_at": str(item.get("published_at") or ""),
                "canonical_url": str(item.get("html_url") or ""),
            }
        )

    if not rows:
        return []

    frame = pl.DataFrame(rows).sort("published_at", descending=True)
    provenance = ReleaseProvenance(
        source_name=raw_capture.source_name,
        raw_path=raw_capture.raw_path,
        fetched_at=raw_capture.fetched_at,
        sha256=raw_capture.sha256,
        checkpoint_token=raw_capture.checkpoint_token,
        adapter_version=ADAPTER_VERSION,
    )
    return [
        NormalizedReleaseRecord(
            canonical_id=row["canonical_id"],
            source_id=row["source_id"],
            owner=row["owner"],
            repo=row["repo"],
            external_slug=row["external_slug"],
            title=row["title"],
            published_at=row["published_at"],
            canonical_url=row["canonical_url"],
            provenance=provenance,
        )
        for row in frame.to_dicts()
    ]


@dataclass(slots=True)
class GitHubReleaseSyncService:
    adapter: SourceAdapter
    archive_root: Path

    def sync_release_page(self, cursor: SyncCursor) -> SyncResult:
        last_error: RetryableFetchError | None = None
        attempts = max(cursor.max_attempts, 1)
        fetch_result: FetchResult | None = None

        for _attempt in range(1, attempts + 1):
            try:
                fetch_result = self.adapter.fetch_release_page(cursor)
                break
            except RetryableFetchError as exc:
                last_error = exc

        if fetch_result is None:
            raise last_error or RetryableFetchError("sync failed without a fetch result")

        raw_capture = archive_raw_capture(self.archive_root, cursor, fetch_result)
        payload = parse_archived_release_payload(raw_capture)
        records = normalize_release_records(raw_capture, payload)
        next_cursor = (
            SyncCursor(
                owner=cursor.owner,
                repo=cursor.repo,
                page=fetch_result.next_page,
                etag=fetch_result.checkpoint_token,
                max_attempts=cursor.max_attempts,
            )
            if fetch_result.next_page is not None
            else None
        )
        return SyncResult(raw_capture=raw_capture, records=records, next_cursor=next_cursor)

    def replay_from_archive(self, raw_capture: RawCapture) -> list[NormalizedReleaseRecord]:
        return normalize_release_records(raw_capture, parse_archived_release_payload(raw_capture))


def get_release_sync_service() -> GitHubReleaseSyncService:
    raise NotImplementedError("Wire a real GitHubReleaseSyncService through FastAPI dependencies.")


@router.post("/github-releases", response_model=SyncReceipt)
def run_github_release_sync(
    owner: str,
    repo: str,
    page: int = 1,
    etag: str | None = None,
    service: GitHubReleaseSyncService = Depends(get_release_sync_service),
) -> SyncReceipt:
    try:
        result = service.sync_release_page(SyncCursor(owner=owner, repo=repo, page=page, etag=etag))
    except RetryableFetchError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return SyncReceipt(
        source_name=SOURCE_NAME,
        raw_path=result.raw_capture.raw_path,
        normalized_count=len(result.records),
        checkpoint_token=result.raw_capture.checkpoint_token,
        next_page=result.next_cursor.page if result.next_cursor else None,
    )
