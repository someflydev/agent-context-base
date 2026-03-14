defmodule Example.Acquisition.SyncCursor do
  @enforce_keys [:owner, :repo]
  defstruct owner: nil, repo: nil, page: 1, etag: nil, max_attempts: 2

  def checkpoint_token(%__MODULE__{etag: etag, page: page}) do
    etag || "page=#{max(page, 1)}"
  end
end

defmodule Example.Acquisition.FetchResult do
  @enforce_keys [
    :body,
    :fetched_at,
    :status_code,
    :content_type,
    :request_url,
    :checkpoint_token
  ]
  defstruct [
    :body,
    :fetched_at,
    :status_code,
    :content_type,
    :request_url,
    :checkpoint_token,
    :next_page
  ]
end

defmodule Example.Acquisition.RawCapture do
  @enforce_keys [:source_name, :owner, :repo, :fetched_at, :raw_path, :metadata_path, :sha256]
  defstruct [
    :source_name,
    :owner,
    :repo,
    :fetched_at,
    :raw_path,
    :metadata_path,
    :sha256,
    :checkpoint_token,
    :request_url
  ]
end

defmodule Example.Acquisition.ReleaseProvenance do
  @enforce_keys [:source_name, :raw_path, :fetched_at, :sha256, :checkpoint_token, :adapter_version]
  defstruct [:source_name, :raw_path, :fetched_at, :sha256, :checkpoint_token, :adapter_version]
end

defmodule Example.Acquisition.NormalizedReleaseRecord do
  @enforce_keys [:canonical_id, :source_id, :owner, :repo, :external_slug, :title, :provenance]
  defstruct [
    :canonical_id,
    :source_id,
    :owner,
    :repo,
    :external_slug,
    :title,
    :published_at,
    :canonical_url,
    :provenance
  ]
end

defmodule Example.Acquisition.SourceAdapter do
  alias Example.Acquisition.{FetchResult, SyncCursor}

  @callback fetch_release_page(SyncCursor.t()) :: {:ok, FetchResult.t()} | {:error, term()}
end

defmodule Example.Acquisition.GitHubReleaseAdapter do
  @behaviour Example.Acquisition.SourceAdapter

  alias Example.Acquisition.{FetchResult, SyncCursor}

  @source_name "github-releases"

  @impl true
  def fetch_release_page(%SyncCursor{} = cursor) do
    page = max(cursor.page, 1)

    request_url =
      "https://api.github.com/repos/#{cursor.owner}/#{cursor.repo}/releases?per_page=50&page=#{page}"

    headers =
      [
        {"accept", "application/vnd.github+json"},
        {"user-agent", "agent-context-base-canonical-example"},
        {"x-github-api-version", "2022-11-28"}
      ]
      |> maybe_put_if_none_match(cursor.etag)

    request = Finch.build(:get, request_url, headers)

    case Finch.request(request, Example.Finch) do
      {:ok, %Finch.Response{status: status}} when status in [429, 500, 502, 503, 504] ->
        {:error, {:retryable, status}}

      {:ok, %Finch.Response{} = response} ->
        checkpoint_token = header_value(response.headers, "etag") || SyncCursor.checkpoint_token(cursor)

        {:ok,
         %FetchResult{
           body: response.body,
           fetched_at: DateTime.utc_now(),
           status_code: response.status,
           content_type: header_value(response.headers, "content-type") || "application/json",
           request_url: request_url,
           checkpoint_token: checkpoint_token,
           next_page: if(String.trim(response.body) == "", do: nil, else: page + 1)
         }}

      {:error, reason} ->
        {:error, {:retryable, reason}}
    end
  end

  defp maybe_put_if_none_match(headers, nil), do: headers
  defp maybe_put_if_none_match(headers, etag), do: [{"if-none-match", etag} | headers]

  defp header_value(headers, name) do
    headers
    |> Enum.find_value(fn {header_name, value} ->
      if String.downcase(header_name) == name, do: value
    end)
  end
end

defmodule Example.Acquisition.GitHubReleaseSyncService do
  alias Example.Acquisition.{
    FetchResult,
    NormalizedReleaseRecord,
    RawCapture,
    ReleaseProvenance,
    SyncCursor
  }

  @source_name "github-releases"
  @adapter_version "github-releases-v1"

  defstruct [:adapter, :archive_root]

  def sync_release_page(%__MODULE__{} = service, %SyncCursor{} = cursor) do
    attempts = max(cursor.max_attempts, 1)

    with {:ok, fetch_result} <- fetch_with_retry(service.adapter, cursor, attempts),
         {:ok, raw_capture} <- archive_raw_capture(service.archive_root, cursor, fetch_result),
         {:ok, payload} <- parse_archived_release_payload(raw_capture) do
      records = normalize_release_records(raw_capture, payload)

      next_cursor =
        if fetch_result.next_page do
          %SyncCursor{
            owner: cursor.owner,
            repo: cursor.repo,
            page: fetch_result.next_page,
            etag: fetch_result.checkpoint_token,
            max_attempts: cursor.max_attempts
          }
        end

      {:ok, %{raw_capture: raw_capture, records: records, next_cursor: next_cursor}}
    end
  end

  def replay_from_archive(%RawCapture{} = raw_capture) do
    with {:ok, payload} <- parse_archived_release_payload(raw_capture) do
      {:ok, normalize_release_records(raw_capture, payload)}
    end
  end

  def archive_raw_capture(archive_root, %SyncCursor{} = cursor, %FetchResult{} = fetch_result) do
    fetch_stamp = Calendar.strftime(fetch_result.fetched_at, "%Y/%m/%d/%H%M%SZ")
    capture_dir = Path.join([archive_root, @source_name, cursor.owner, cursor.repo, fetch_stamp])
    raw_path = Path.join(capture_dir, "page-#{max(cursor.page, 1)}.json")
    metadata_path = Path.join(capture_dir, "page-#{max(cursor.page, 1)}.metadata.json")

    capture = %RawCapture{
      source_name: @source_name,
      owner: cursor.owner,
      repo: cursor.repo,
      fetched_at: DateTime.to_iso8601(fetch_result.fetched_at),
      raw_path: raw_path,
      metadata_path: metadata_path,
      sha256: :crypto.hash(:sha256, fetch_result.body) |> Base.encode16(case: :lower),
      checkpoint_token: fetch_result.checkpoint_token,
      request_url: fetch_result.request_url
    }

    with :ok <- File.mkdir_p(capture_dir),
         :ok <- File.write(raw_path, fetch_result.body),
         :ok <- File.write(metadata_path, Jason.encode!(Map.from_struct(capture), pretty: true)) do
      {:ok, capture}
    end
  end

  def parse_archived_release_payload(%RawCapture{raw_path: raw_path}) do
    case File.read(raw_path) do
      {:ok, payload} ->
        with {:ok, decoded} <- Jason.decode(payload) do
          {:ok, Enum.filter(decoded, &is_map/1)}
        end

      error ->
        error
    end
  end

  def normalize_release_records(%RawCapture{} = raw_capture, payload) when is_list(payload) do
    provenance = %ReleaseProvenance{
      source_name: raw_capture.source_name,
      raw_path: raw_capture.raw_path,
      fetched_at: raw_capture.fetched_at,
      sha256: raw_capture.sha256,
      checkpoint_token: raw_capture.checkpoint_token,
      adapter_version: @adapter_version
    }

    payload
    |> Enum.reject(&Map.get(&1, "draft", false))
    |> Enum.map(fn item ->
      external_slug = Map.get(item, "tag_name", "")
      title = Map.get(item, "name") || external_slug || "untitled-release"

      %NormalizedReleaseRecord{
        canonical_id: "#{@source_name}:#{raw_capture.owner}/#{raw_capture.repo}:#{Map.get(item, "id")}",
        source_id: Map.get(item, "id"),
        owner: raw_capture.owner,
        repo: raw_capture.repo,
        external_slug: external_slug,
        title: title,
        published_at: Map.get(item, "published_at", ""),
        canonical_url: Map.get(item, "html_url", ""),
        provenance: provenance
      }
    end)
    |> Enum.sort_by(& &1.published_at, :desc)
  end

  defp fetch_with_retry(adapter, cursor, attempts) do
    Enum.reduce_while(1..attempts, {:error, {:retryable, :unknown}}, fn attempt, _acc ->
      case adapter.fetch_release_page(cursor) do
        {:ok, fetch_result} ->
          {:halt, {:ok, fetch_result}}

        {:error, {:retryable, _reason} = error} ->
          Process.sleep(150 * attempt)
          {:cont, {:error, error}}

        {:error, error} ->
          {:halt, {:error, error}}
      end
    end)
  end
end

defmodule ExampleWeb.SourceSyncController do
  use ExampleWeb, :controller

  alias Example.Acquisition.{GitHubReleaseAdapter, GitHubReleaseSyncService, SyncCursor}

  def create(conn, %{"owner" => owner, "repo" => repo} = params) do
    cursor = %SyncCursor{
      owner: owner,
      repo: repo,
      page: parse_integer(Map.get(params, "page"), 1),
      etag: Map.get(params, "etag"),
      max_attempts: parse_integer(Map.get(params, "max_attempts"), 2)
    }

    service = %GitHubReleaseSyncService{
      adapter: GitHubReleaseAdapter,
      archive_root: "./data/raw"
    }

    with {:ok, result} <- GitHubReleaseSyncService.sync_release_page(service, cursor) do
      conn
      |> put_status(:accepted)
      |> json(%{
        source_name: "github-releases",
        raw_path: result.raw_capture.raw_path,
        normalized_count: length(result.records),
        checkpoint_token: result.raw_capture.checkpoint_token,
        next_page: result.next_cursor && result.next_cursor.page
      })
    end
  end

  defp parse_integer(nil, default), do: default

  defp parse_integer(raw, default) do
    case Integer.parse(raw) do
      {value, _rest} -> value
      :error -> default
    end
  end
end
