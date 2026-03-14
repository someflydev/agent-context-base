use async_trait::async_trait;
use axum::{
    extract::{Json, Path, State},
    http::StatusCode,
    routing::post,
    Router,
};
use reqwest::header::{ACCEPT, CONTENT_TYPE, ETAG, IF_NONE_MATCH, USER_AGENT};
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::path::{Path as StdPath, PathBuf};
use std::sync::Arc;
use time::{format_description::well_known::Rfc3339, OffsetDateTime};
use tokio::fs;

const SOURCE_NAME: &str = "github-releases";
const ADAPTER_VERSION: &str = "github-releases-v1";

#[derive(Clone)]
pub struct AppState {
    pub sync_service: Arc<GitHubReleaseSyncService>,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct SyncCursor {
    pub owner: String,
    pub repo: String,
    pub page: u32,
    pub etag: Option<String>,
    pub max_attempts: u8,
}

impl SyncCursor {
    pub fn checkpoint_token(&self) -> String {
        self.etag
            .clone()
            .unwrap_or_else(|| format!("page={}", self.page.max(1)))
    }
}

#[derive(Clone, Debug)]
pub struct FetchResult {
    pub body: Vec<u8>,
    pub fetched_at: OffsetDateTime,
    pub status_code: StatusCode,
    pub content_type: String,
    pub request_url: String,
    pub checkpoint_token: String,
    pub next_page: Option<u32>,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct RawCapture {
    pub source_name: String,
    pub owner: String,
    pub repo: String,
    pub fetched_at: String,
    pub raw_path: String,
    pub metadata_path: String,
    pub sha256: String,
    pub checkpoint_token: String,
    pub request_url: String,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct ReleaseProvenance {
    pub source_name: String,
    pub raw_path: String,
    pub fetched_at: String,
    pub sha256: String,
    pub checkpoint_token: String,
    pub adapter_version: String,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct NormalizedReleaseRecord {
    pub canonical_id: String,
    pub source_id: i64,
    pub owner: String,
    pub repo: String,
    pub tag_name: String,
    pub title: String,
    pub published_at: String,
    pub html_url: String,
    pub provenance: ReleaseProvenance,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct SyncReceipt {
    pub source_name: String,
    pub raw_path: String,
    pub normalized_count: usize,
    pub checkpoint_token: String,
    pub next_page: Option<u32>,
}

#[derive(Clone, Debug)]
pub struct SyncResult {
    pub raw_capture: RawCapture,
    pub records: Vec<NormalizedReleaseRecord>,
    pub next_cursor: Option<SyncCursor>,
}

#[derive(Debug)]
pub struct RetryableFetchError {
    pub message: String,
}

impl std::fmt::Display for RetryableFetchError {
    fn fmt(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(formatter, "{}", self.message)
    }
}

impl std::error::Error for RetryableFetchError {}

#[async_trait]
pub trait SourceAdapter: Send + Sync {
    async fn fetch_release_page(&self, cursor: &SyncCursor) -> anyhow::Result<FetchResult>;
}

pub struct GitHubReleaseAdapter {
    pub client: reqwest::Client,
}

#[async_trait]
impl SourceAdapter for GitHubReleaseAdapter {
    async fn fetch_release_page(&self, cursor: &SyncCursor) -> anyhow::Result<FetchResult> {
        let page = cursor.page.max(1);
        let request_url = format!(
            "https://api.github.com/repos/{}/{}/releases?per_page=50&page={page}",
            cursor.owner, cursor.repo,
        );

        let mut request = self
            .client
            .get(&request_url)
            .header(ACCEPT, "application/vnd.github+json")
            .header(USER_AGENT, "agent-context-base-canonical-example")
            .header("X-GitHub-Api-Version", "2022-11-28");
        if let Some(etag) = &cursor.etag {
            request = request.header(IF_NONE_MATCH, etag);
        }

        let response = request.send().await.map_err(|error| RetryableFetchError {
            message: format!("transient upstream network failure: {error}"),
        })?;

        if response.status() == StatusCode::TOO_MANY_REQUESTS || response.status().is_server_error()
        {
            return Err(RetryableFetchError {
                message: format!("retryable upstream status {}", response.status()),
            }
            .into());
        }

        let status_code = response.status();
        let content_type = response
            .headers()
            .get(CONTENT_TYPE)
            .and_then(|value| value.to_str().ok())
            .unwrap_or("application/json")
            .to_string();
        let checkpoint_token = response
            .headers()
            .get(ETAG)
            .and_then(|value| value.to_str().ok())
            .map(str::to_string)
            .unwrap_or_else(|| cursor.checkpoint_token());
        let body = response.bytes().await?.to_vec();

        Ok(FetchResult {
            body: body.clone(),
            fetched_at: OffsetDateTime::now_utc(),
            status_code,
            content_type,
            request_url,
            checkpoint_token,
            next_page: if body.is_empty() {
                None
            } else {
                Some(page + 1)
            },
        })
    }
}

#[derive(Clone, Debug, Deserialize)]
struct GitHubReleasePayload {
    id: i64,
    tag_name: String,
    name: Option<String>,
    html_url: String,
    published_at: Option<String>,
    draft: bool,
}

pub async fn archive_raw_capture(
    archive_root: &StdPath,
    cursor: &SyncCursor,
    fetch_result: &FetchResult,
) -> anyhow::Result<RawCapture> {
    let timestamp = fetch_result
        .fetched_at
        .format(&Rfc3339)?
        .replace([':', '-'], "");
    let capture_dir = archive_root
        .join(SOURCE_NAME)
        .join(&cursor.owner)
        .join(&cursor.repo)
        .join(timestamp);
    fs::create_dir_all(&capture_dir).await?;

    let page = cursor.page.max(1);
    let raw_path = capture_dir.join(format!("page-{page}.json"));
    let metadata_path = capture_dir.join(format!("page-{page}.metadata.json"));
    fs::write(&raw_path, &fetch_result.body).await?;

    let sha256 = format!("{:x}", Sha256::digest(&fetch_result.body));
    let capture = RawCapture {
        source_name: SOURCE_NAME.to_string(),
        owner: cursor.owner.clone(),
        repo: cursor.repo.clone(),
        fetched_at: fetch_result.fetched_at.format(&Rfc3339)?,
        raw_path: raw_path.display().to_string(),
        metadata_path: metadata_path.display().to_string(),
        sha256,
        checkpoint_token: fetch_result.checkpoint_token.clone(),
        request_url: fetch_result.request_url.clone(),
    };
    fs::write(&metadata_path, serde_json::to_vec_pretty(&capture)?).await?;
    Ok(capture)
}

pub fn parse_archived_release_payload(
    raw_bytes: &[u8],
) -> anyhow::Result<Vec<GitHubReleasePayload>> {
    Ok(serde_json::from_slice(raw_bytes)?)
}

pub fn normalize_release_records(
    raw_capture: &RawCapture,
    payload: Vec<GitHubReleasePayload>,
) -> Vec<NormalizedReleaseRecord> {
    let provenance = ReleaseProvenance {
        source_name: raw_capture.source_name.clone(),
        raw_path: raw_capture.raw_path.clone(),
        fetched_at: raw_capture.fetched_at.clone(),
        sha256: raw_capture.sha256.clone(),
        checkpoint_token: raw_capture.checkpoint_token.clone(),
        adapter_version: ADAPTER_VERSION.to_string(),
    };

    payload
        .into_iter()
        .filter(|item| !item.draft)
        .map(|item| NormalizedReleaseRecord {
            canonical_id: format!(
                "{SOURCE_NAME}:{}/{}:{}",
                raw_capture.owner, raw_capture.repo, item.id
            ),
            source_id: item.id,
            owner: raw_capture.owner.clone(),
            repo: raw_capture.repo.clone(),
            tag_name: item.tag_name.clone(),
            title: item.name.unwrap_or_else(|| item.tag_name.clone()),
            published_at: item.published_at.unwrap_or_default(),
            html_url: item.html_url,
            provenance: provenance.clone(),
        })
        .collect()
}

pub struct GitHubReleaseSyncService {
    pub adapter: Arc<dyn SourceAdapter>,
    pub archive_root: PathBuf,
}

impl GitHubReleaseSyncService {
    pub async fn sync_release_page(&self, cursor: SyncCursor) -> anyhow::Result<SyncResult> {
        let mut last_error: Option<anyhow::Error> = None;
        let attempts = cursor.max_attempts.max(1);
        let mut fetch_result: Option<FetchResult> = None;

        for _attempt in 1..=attempts {
            match self.adapter.fetch_release_page(&cursor).await {
                Ok(result) => {
                    fetch_result = Some(result);
                    break;
                }
                Err(error) => last_error = Some(error),
            }
        }

        let fetch_result = match fetch_result {
            Some(result) => result,
            None => {
                return Err(last_error
                    .unwrap_or_else(|| anyhow::anyhow!("sync failed without a fetch result")))
            }
        };

        let raw_capture = archive_raw_capture(&self.archive_root, &cursor, &fetch_result).await?;
        let raw_bytes = fs::read(&raw_capture.raw_path).await?;
        let payload = parse_archived_release_payload(&raw_bytes)?;
        let records = normalize_release_records(&raw_capture, payload);
        let next_cursor = fetch_result.next_page.map(|next_page| SyncCursor {
            owner: cursor.owner.clone(),
            repo: cursor.repo.clone(),
            page: next_page,
            etag: Some(fetch_result.checkpoint_token.clone()),
            max_attempts: cursor.max_attempts,
        });

        Ok(SyncResult {
            raw_capture,
            records,
            next_cursor,
        })
    }

    pub async fn replay_from_archive(
        &self,
        raw_capture: &RawCapture,
    ) -> anyhow::Result<Vec<NormalizedReleaseRecord>> {
        let raw_bytes = fs::read(&raw_capture.raw_path).await?;
        let payload = parse_archived_release_payload(&raw_bytes)?;
        Ok(normalize_release_records(raw_capture, payload))
    }
}

pub fn router(state: AppState) -> Router {
    Router::new()
        .route("/sources/github-releases/:owner/:repo/sync", post(run_sync))
        .with_state(state)
}

#[derive(Debug, Deserialize)]
pub struct SyncRequest {
    pub page: Option<u32>,
    pub etag: Option<String>,
    pub max_attempts: Option<u8>,
}

async fn run_sync(
    State(state): State<AppState>,
    Path((owner, repo)): Path<(String, String)>,
    Json(request): Json<SyncRequest>,
) -> Result<Json<SyncReceipt>, (StatusCode, String)> {
    let cursor = SyncCursor {
        owner,
        repo,
        page: request.page.unwrap_or(1),
        etag: request.etag,
        max_attempts: request.max_attempts.unwrap_or(2),
    };

    let result = state
        .sync_service
        .sync_release_page(cursor)
        .await
        .map_err(|error| (StatusCode::BAD_GATEWAY, error.to_string()))?;

    Ok(Json(SyncReceipt {
        source_name: SOURCE_NAME.to_string(),
        raw_path: result.raw_capture.raw_path,
        normalized_count: result.records.len(),
        checkpoint_token: result.raw_capture.checkpoint_token,
        next_page: result.next_cursor.map(|cursor| cursor.page),
    }))
}
