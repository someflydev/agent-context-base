require "json"
require "digest"
require "fileutils"
require "net/http"
require "sequel"
require "time"
require "tmpdir"
require "uri"

require "hanami/action"
require "hanami/router"

module RubyHanamiSourceSyncExample
  SOURCE_NAME = "github-releases"
  ADAPTER_VERSION = "github-releases-v1"
  DB = Sequel.sqlite

  SyncCursor = Struct.new(:owner, :repo, :page, :etag, keyword_init: true) do
    def checkpoint_token
      etag || "page=#{page || 1}"
    end
  end

  FetchResult = Struct.new(
    :body,
    :fetched_at,
    :status_code,
    :request_url,
    :checkpoint_token,
    :next_page,
    keyword_init: true,
  )

  RawCapture = Struct.new(
    :source_name,
    :owner,
    :repo,
    :fetched_at,
    :raw_path,
    :metadata_path,
    :checksum,
    :checkpoint_token,
    :request_url,
    keyword_init: true,
  ) do
    def to_h
      {
        source_name: source_name,
        owner: owner,
        repo: repo,
        fetched_at: fetched_at,
        raw_path: raw_path,
        metadata_path: metadata_path,
        checksum: checksum,
        checkpoint_token: checkpoint_token,
        request_url: request_url,
      }
    end
  end

  ReleaseProvenance = Struct.new(
    :source_name,
    :raw_path,
    :fetched_at,
    :checksum,
    :checkpoint_token,
    :adapter_version,
    keyword_init: true,
  ) do
    def to_h
      {
        source_name: source_name,
        raw_path: raw_path,
        fetched_at: fetched_at,
        checksum: checksum,
        checkpoint_token: checkpoint_token,
        adapter_version: adapter_version,
      }
    end
  end

  NormalizedReleaseRecord = Struct.new(
    :canonical_id,
    :source_id,
    :owner,
    :repo,
    :tag_name,
    :title,
    :published_at,
    :release_url,
    :provenance,
    keyword_init: true,
  ) do
    def to_h
      {
        canonical_id: canonical_id,
        source_id: source_id,
        owner: owner,
        repo: repo,
        tag_name: tag_name,
        title: title,
        published_at: published_at,
        release_url: release_url,
        provenance: provenance.to_h,
      }
    end
  end

  SyncReceipt = Struct.new(
    :source_name,
    :raw_capture_path,
    :normalized_count,
    :checkpoint_token,
    :next_page,
    keyword_init: true,
  ) do
    def to_h
      {
        source_name: source_name,
        raw_capture_path: raw_capture_path,
        normalized_count: normalized_count,
        checkpoint_token: checkpoint_token,
        next_page: next_page,
      }
    end
  end

  class SourceCheckpointsRepo
    class << self
      def load(owner:, repo:)
        prepare!
        row = DB[:source_checkpoints].where(source_name: SOURCE_NAME, owner: owner, repo: repo).first
        return nil unless row

        SyncCursor.new(
          owner: owner,
          repo: repo,
          page: row[:page],
          etag: row[:checkpoint_token],
        )
      end

      def save(cursor)
        prepare!
        dataset = DB[:source_checkpoints].where(
          source_name: SOURCE_NAME,
          owner: cursor.owner,
          repo: cursor.repo,
        )

        if dataset.count.zero?
          DB[:source_checkpoints].insert(
            source_name: SOURCE_NAME,
            owner: cursor.owner,
            repo: cursor.repo,
            page: cursor.page,
            checkpoint_token: cursor.checkpoint_token,
          )
        else
          dataset.update(page: cursor.page, checkpoint_token: cursor.checkpoint_token)
        end
      end

      private

      def prepare!
        return if @prepared

        DB.create_table?(:source_checkpoints) do
          primary_key :id
          String :source_name, null: false
          String :owner, null: false
          String :repo, null: false
          Integer :page, null: false
          String :checkpoint_token, null: false
          index %i[source_name owner repo], unique: true
        end

        @prepared = true
      end
    end
  end

  class NormalizedReleasesRepo
    class << self
      def upsert(records)
        prepare!

        records.each do |record|
          dataset = DB[:normalized_releases].where(canonical_id: record.canonical_id)
          payload = {
            canonical_id: record.canonical_id,
            source_id: record.source_id,
            owner: record.owner,
            repo: record.repo,
            tag_name: record.tag_name,
            title: record.title,
            published_at: record.published_at,
            release_url: record.release_url,
            provenance_json: JSON.generate(record.provenance.to_h),
          }

          if dataset.count.zero?
            DB[:normalized_releases].insert(payload)
          else
            dataset.update(payload)
          end
        end
      end

      private

      def prepare!
        return if @prepared

        DB.create_table?(:normalized_releases) do
          primary_key :id
          String :canonical_id, null: false
          Integer :source_id, null: false
          String :owner, null: false
          String :repo, null: false
          String :tag_name, null: false
          String :title, null: false
          String :published_at, null: false
          String :release_url, null: false
          String :provenance_json, text: true, null: false
          index :canonical_id, unique: true
        end

        @prepared = true
      end
    end
  end

  class GitHubReleaseAdapter
    def fetch_release_page(cursor)
      page = [cursor.page || 1, 1].max
      uri = URI("https://api.github.com/repos/#{cursor.owner}/#{cursor.repo}/releases?per_page=50&page=#{page}")
      request = Net::HTTP::Get.new(uri)
      request["Accept"] = "application/vnd.github+json"
      request["User-Agent"] = "agent-context-base-canonical-example"
      request["X-GitHub-Api-Version"] = "2022-11-28"
      request["If-None-Match"] = cursor.etag if cursor.etag

      response = Net::HTTP.start(uri.host, uri.port, use_ssl: true) { |http| http.request(request) }

      FetchResult.new(
        body: response.body.to_s,
        fetched_at: Time.now.utc.iso8601,
        status_code: response.code.to_i,
        request_url: uri.to_s,
        checkpoint_token: response["etag"] || cursor.checkpoint_token,
        next_page: response.body.to_s.strip.empty? ? nil : page + 1,
      )
    end
  end

  class ArchiveStore
    def initialize(root:)
      @root = root
    end

    def archive_raw_capture(cursor, fetch_result)
      fetch_stamp = fetch_result.fetched_at.delete(":")
      capture_dir = File.join(@root, SOURCE_NAME, cursor.owner, cursor.repo, fetch_stamp)
      FileUtils.mkdir_p(capture_dir)

      raw_path = File.join(capture_dir, "page-#{cursor.page}.json")
      metadata_path = File.join(capture_dir, "page-#{cursor.page}.metadata.json")
      File.write(raw_path, fetch_result.body)

      raw_capture = RawCapture.new(
        source_name: SOURCE_NAME,
        owner: cursor.owner,
        repo: cursor.repo,
        fetched_at: fetch_result.fetched_at,
        raw_path: raw_path,
        metadata_path: metadata_path,
        checksum: Digest::SHA256.hexdigest(fetch_result.body),
        checkpoint_token: fetch_result.checkpoint_token,
        request_url: fetch_result.request_url,
      )

      File.write(metadata_path, JSON.pretty_generate(raw_capture.to_h))
      raw_capture
    end

    def parse_archived_release_payload(raw_capture)
      payload = JSON.parse(File.read(raw_capture.raw_path))
      raise ArgumentError, "GitHub releases payload must be a JSON array" unless payload.is_a?(Array)

      payload.grep(Hash)
    end
  end

  class NormalizeReleasePayload
    def call(raw_capture:, payload:)
      provenance = ReleaseProvenance.new(
        source_name: raw_capture.source_name,
        raw_path: raw_capture.raw_path,
        fetched_at: raw_capture.fetched_at,
        checksum: raw_capture.checksum,
        checkpoint_token: raw_capture.checkpoint_token,
        adapter_version: ADAPTER_VERSION,
      )

      payload
        .reject { |item| item["draft"] }
        .map do |item|
          NormalizedReleaseRecord.new(
            canonical_id: "#{SOURCE_NAME}:#{raw_capture.owner}/#{raw_capture.repo}:#{item.fetch("id")}",
            source_id: Integer(item.fetch("id")),
            owner: raw_capture.owner,
            repo: raw_capture.repo,
            tag_name: item.fetch("tag_name", ""),
            title: item["name"].to_s.empty? ? item.fetch("tag_name", "untitled-release") : item["name"],
            published_at: item.fetch("published_at", ""),
            release_url: item.fetch("html_url", ""),
            provenance: provenance,
          )
        end
        .sort_by(&:published_at)
        .reverse
    end
  end

  class SyncGitHubReleases
    def initialize(
      source_client: GitHubReleaseAdapter.new,
      archive_store: ArchiveStore.new(root: Dir.mktmpdir("hanami-source-sync")),
      checkpoints: SourceCheckpointsRepo,
      normalized_releases: NormalizedReleasesRepo,
      normalizer: NormalizeReleasePayload.new,
    )
      @source_client = source_client
      @archive_store = archive_store
      @checkpoints = checkpoints
      @normalized_releases = normalized_releases
      @normalizer = normalizer
    end

    def call(owner:, repo:, requested_page: nil)
      stored_cursor = @checkpoints.load(owner: owner, repo: repo)
      cursor = if stored_cursor
        SyncCursor.new(owner: owner, repo: repo, page: requested_page || stored_cursor.page, etag: stored_cursor.etag)
      else
        SyncCursor.new(owner: owner, repo: repo, page: requested_page || 1, etag: nil)
      end

      fetch_result = @source_client.fetch_release_page(cursor)
      raw_capture = @archive_store.archive_raw_capture(cursor, fetch_result)
      records = replay_from_archive(raw_capture)

      if fetch_result.next_page
        @checkpoints.save(
          SyncCursor.new(
            owner: owner,
            repo: repo,
            page: fetch_result.next_page,
            etag: fetch_result.checkpoint_token,
          ),
        )
      end

      @normalized_releases.upsert(records)

      SyncReceipt.new(
        source_name: raw_capture.source_name,
        raw_capture_path: raw_capture.raw_path,
        normalized_count: records.length,
        checkpoint_token: raw_capture.checkpoint_token,
        next_page: fetch_result.next_page,
      )
    end

    def replay_from_archive(raw_capture)
      payload = @archive_store.parse_archived_release_payload(raw_capture)
      @normalizer.call(raw_capture: raw_capture, payload: payload)
    end
  end

  class SourceSyncAction < Hanami::Action
    def initialize(sync_service: SyncGitHubReleases.new)
      super()
      @sync_service = sync_service
    end

    def handle(request, response)
      receipt = @sync_service.call(
        owner: request.params[:owner].to_s,
        repo: request.params[:repo].to_s,
        requested_page: integer_param(request.params[:page]),
      )

      response.format = :json
      response.body = JSON.generate(receipt.to_h)
    end

    private

    def integer_param(value)
      Integer(value)
    rescue ArgumentError, TypeError
      nil
    end
  end

  Routes = Hanami::Router.new do
    post "/source-sync/:owner/:repo", to: SourceSyncAction.new
  end
end
