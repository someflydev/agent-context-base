require "json"
require "kemal"
require "avram"
require "http/client"
require "digest/sha256"
require "file_utils"

SOURCE_NAME = "github-releases"
ADAPTER_VERSION = "github-releases-v1"

class RetryableFetchError < Exception
end

class SourceCheckpoint < BaseModel
  table do
    column source_name : String
    column repo_key : String
    column checkpoint_token : String
  end
end

class SourceCheckpointQuery < SourceCheckpoint::BaseQuery
  def for_repo(owner : String, repo : String)
    source_name(SOURCE_NAME).repo_key("#{owner}/#{repo}")
  end
end

struct SyncCursor
  getter owner : String
  getter repo : String
  getter page : Int32
  getter etag : String?
  getter max_attempts : Int32

  def initialize(@owner : String, @repo : String, @page : Int32 = 1, @etag : String? = nil, @max_attempts : Int32 = 2)
  end

  def checkpoint_token : String
    etag || "page=#{page < 1 ? 1 : page}"
  end
end

struct FetchResult
  getter body : String
  getter fetched_at : Time
  getter status_code : Int32
  getter content_type : String
  getter request_url : String
  getter checkpoint_token : String
  getter next_page : Int32?

  def initialize(
    @body : String,
    @fetched_at : Time,
    @status_code : Int32,
    @content_type : String,
    @request_url : String,
    @checkpoint_token : String,
    @next_page : Int32?
  )
  end
end

struct RawCapture
  include JSON::Serializable

  getter source_name : String
  getter owner : String
  getter repo : String
  getter fetched_at : String
  getter raw_path : String
  getter metadata_path : String
  getter sha256 : String
  getter checkpoint_token : String
  getter request_url : String

  def initialize(
    @source_name : String,
    @owner : String,
    @repo : String,
    @fetched_at : String,
    @raw_path : String,
    @metadata_path : String,
    @sha256 : String,
    @checkpoint_token : String,
    @request_url : String
  )
  end
end

struct ReleaseProvenance
  include JSON::Serializable

  getter source_name : String
  getter raw_path : String
  getter fetched_at : String
  getter sha256 : String
  getter checkpoint_token : String
  getter adapter_version : String

  def initialize(
    @source_name : String,
    @raw_path : String,
    @fetched_at : String,
    @sha256 : String,
    @checkpoint_token : String,
    @adapter_version : String
  )
  end
end

struct NormalizedReleaseRecord
  include JSON::Serializable

  getter canonical_id : String
  getter source_id : Int64
  getter owner : String
  getter repo : String
  getter external_slug : String
  getter title : String
  getter published_at : String
  getter canonical_url : String
  getter provenance : ReleaseProvenance

  def initialize(
    @canonical_id : String,
    @source_id : Int64,
    @owner : String,
    @repo : String,
    @external_slug : String,
    @title : String,
    @published_at : String,
    @canonical_url : String,
    @provenance : ReleaseProvenance
  )
  end
end

struct SyncResult
  getter raw_capture : RawCapture
  getter records : Array(NormalizedReleaseRecord)
  getter next_cursor : SyncCursor?

  def initialize(@raw_capture : RawCapture, @records : Array(NormalizedReleaseRecord), @next_cursor : SyncCursor?)
  end
end

struct SyncReceipt
  include JSON::Serializable

  getter source_name : String
  getter raw_path : String
  getter normalized_count : Int32
  getter checkpoint_token : String
  getter next_page : Int32?

  def initialize(
    @source_name : String,
    @raw_path : String,
    @normalized_count : Int32,
    @checkpoint_token : String,
    @next_page : Int32?
  )
  end
end

struct GitHubReleasePayload
  include JSON::Serializable

  getter id : Int64
  getter tag_name : String
  getter name : String?
  getter html_url : String
  getter published_at : String?
  getter draft : Bool = false
end

abstract class SourceAdapter
  abstract def fetch_release_page(cursor : SyncCursor) : FetchResult
end

class GitHubReleaseAdapter < SourceAdapter
  def fetch_release_page(cursor : SyncCursor) : FetchResult
    page = cursor.page < 1 ? 1 : cursor.page
    request_url = "https://api.github.com/repos/#{cursor.owner}/#{cursor.repo}/releases?per_page=50&page=#{page}"
    headers = HTTP::Headers{
      "Accept" => "application/vnd.github+json",
      "User-Agent" => "agent-context-base-canonical-example",
      "X-GitHub-Api-Version" => "2022-11-28",
    }
    headers["If-None-Match"] = cursor.etag.not_nil! if cursor.etag

    response = HTTP::Client.get(request_url, headers: headers)
    if response.status_code == 429 || response.status_code >= 500
      raise RetryableFetchError.new("retryable upstream status #{response.status_code}")
    end

    FetchResult.new(
      body: response.body,
      fetched_at: Time.utc,
      status_code: response.status_code,
      content_type: response.headers["Content-Type"]? || "application/json",
      request_url: request_url,
      checkpoint_token: response.headers["ETag"]? || cursor.checkpoint_token,
      next_page: response.body.empty? ? nil : page + 1
    )
  rescue Socket::Error
    raise RetryableFetchError.new("transient upstream network failure")
  end
end

def archive_raw_capture(archive_root : String, cursor : SyncCursor, fetch_result : FetchResult) : RawCapture
  fetch_stamp = fetch_result.fetched_at.to_s("%Y/%m/%d/%H%M%SZ")
  capture_dir = File.join(archive_root, SOURCE_NAME, cursor.owner, cursor.repo, fetch_stamp)
  FileUtils.mkdir_p(capture_dir)

  page = cursor.page < 1 ? 1 : cursor.page
  raw_path = File.join(capture_dir, "page-#{page}.json")
  metadata_path = File.join(capture_dir, "page-#{page}.metadata.json")
  File.write(raw_path, fetch_result.body)

  capture = RawCapture.new(
    source_name: SOURCE_NAME,
    owner: cursor.owner,
    repo: cursor.repo,
    fetched_at: fetch_result.fetched_at.to_rfc3339,
    raw_path: raw_path,
    metadata_path: metadata_path,
    sha256: Digest::SHA256.hexdigest(fetch_result.body),
    checkpoint_token: fetch_result.checkpoint_token,
    request_url: fetch_result.request_url
  )

  File.write(metadata_path, capture.to_json)
  capture
end

def parse_archived_release_payload(raw_capture : RawCapture) : Array(GitHubReleasePayload)
  Array(GitHubReleasePayload).from_json(File.read(raw_capture.raw_path))
end

def normalize_release_records(raw_capture : RawCapture, payload : Array(GitHubReleasePayload)) : Array(NormalizedReleaseRecord)
  provenance = ReleaseProvenance.new(
    source_name: raw_capture.source_name,
    raw_path: raw_capture.raw_path,
    fetched_at: raw_capture.fetched_at,
    sha256: raw_capture.sha256,
    checkpoint_token: raw_capture.checkpoint_token,
    adapter_version: ADAPTER_VERSION
  )

  payload.compact_map do |item|
    next if item.draft

    external_slug = item.tag_name
    title = item.name.presence || external_slug

    NormalizedReleaseRecord.new(
      canonical_id: "#{SOURCE_NAME}:#{raw_capture.owner}/#{raw_capture.repo}:#{item.id}",
      source_id: item.id,
      owner: raw_capture.owner,
      repo: raw_capture.repo,
      external_slug: external_slug,
      title: title,
      published_at: item.published_at || "",
      canonical_url: item.html_url,
      provenance: provenance
    )
  end
end

class GitHubReleaseSyncService
  def initialize(@adapter : SourceAdapter, @archive_root : String)
  end

  def sync_release_page(cursor : SyncCursor) : SyncResult
    attempts = cursor.max_attempts < 1 ? 1 : cursor.max_attempts
    fetch_result = nil
    last_error = nil

    attempts.times do
      begin
        fetch_result = @adapter.fetch_release_page(cursor)
        break
      rescue RetryableFetchError => error
        last_error = error
      end
    end

    resolved_fetch = fetch_result || raise(last_error || RetryableFetchError.new("sync failed without a fetch result"))
    raw_capture = archive_raw_capture(@archive_root, cursor, resolved_fetch)
    payload = parse_archived_release_payload(raw_capture)
    records = normalize_release_records(raw_capture, payload)
    next_cursor = if next_page = resolved_fetch.next_page
      SyncCursor.new(cursor.owner, cursor.repo, next_page, resolved_fetch.checkpoint_token, cursor.max_attempts)
    end

    SyncResult.new(raw_capture, records, next_cursor)
  end

  def replay_from_archive(raw_capture : RawCapture) : Array(NormalizedReleaseRecord)
    normalize_release_records(raw_capture, parse_archived_release_payload(raw_capture))
  end
end

post "/sources/github-releases/:owner/:repo/sync" do |env|
  owner = env.params.url["owner"]
  repo = env.params.url["repo"]
  stored_checkpoint = SourceCheckpointQuery.new.for_repo(owner, repo).first?.try(&.checkpoint_token)
  service = GitHubReleaseSyncService.new(GitHubReleaseAdapter.new, "./data/raw")

  result = service.sync_release_page(
    SyncCursor.new(
      owner: owner,
      repo: repo,
      page: 1,
      etag: stored_checkpoint,
      max_attempts: 2
    )
  )

  env.response.status_code = 202
  env.response.content_type = "application/json"
  SyncReceipt.new(
    source_name: SOURCE_NAME,
    raw_path: result.raw_capture.raw_path,
    normalized_count: result.records.size,
    checkpoint_token: result.raw_capture.checkpoint_token,
    next_page: result.next_cursor.try(&.page)
  ).to_json
end
