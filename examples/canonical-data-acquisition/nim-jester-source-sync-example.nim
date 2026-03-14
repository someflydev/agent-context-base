import std/[json, times, strformat, os, options, httpclient]
import jester

const
  SourceName* = "github-releases"
  AdapterVersion* = "github-releases-v1"

type
  RetryableFetchError* = object of CatchableError

  SyncCursor* = object
    owner*: string
    repo*: string
    page*: int
    etag*: Option[string]
    maxAttempts*: int

  FetchResult* = object
    body*: string
    fetchedAt*: Time
    statusCode*: int
    contentType*: string
    requestUrl*: string
    checkpointToken*: string
    nextPage*: Option[int]

  RawCapture* = object
    sourceName*: string
    owner*: string
    repo*: string
    fetchedAt*: string
    rawPath*: string
    metadataPath*: string
    sha256*: string
    checkpointToken*: string
    requestUrl*: string

  ReleaseProvenance* = object
    sourceName*: string
    rawPath*: string
    fetchedAt*: string
    sha256*: string
    checkpointToken*: string
    adapterVersion*: string

  NormalizedReleaseRecord* = object
    canonicalId*: string
    sourceId*: int
    owner*: string
    repo*: string
    externalSlug*: string
    title*: string
    publishedAt*: string
    canonicalUrl*: string
    provenance*: ReleaseProvenance

  SyncResult* = object
    rawCapture*: RawCapture
    records*: seq[NormalizedReleaseRecord]
    nextCursor*: Option[SyncCursor]

  SourceAdapter* = ref object
    client*: HttpClient

  GitHubReleaseSyncService* = ref object
    adapter*: SourceAdapter
    archiveRoot*: string

proc checkpointToken*(cursor: SyncCursor): string =
  if cursor.etag.isSome:
    cursor.etag.get()
  else:
    fmt"page={max(cursor.page, 1)}"

proc fetchReleasePage*(adapter: SourceAdapter, cursor: SyncCursor): FetchResult =
  let page = max(cursor.page, 1)
  let requestUrl = fmt"https://api.github.com/repos/{cursor.owner}/{cursor.repo}/releases?per_page=50&page={page}"
  var headers = newHttpHeaders()
  headers["Accept"] = "application/vnd.github+json"
  headers["User-Agent"] = "agent-context-base-canonical-example"
  headers["X-GitHub-Api-Version"] = "2022-11-28"
  if cursor.etag.isSome:
    headers["If-None-Match"] = cursor.etag.get()

  let response = adapter.client.request(requestUrl, httpMethod = HttpGet, headers = headers)
  let statusCode = int(response.code)
  if statusCode == 429 or statusCode >= 500:
    raise newException(RetryableFetchError, fmt"retryable upstream status {statusCode}")

  let checkpoint = if response.headers.hasKey("ETag"): response.headers["ETag"] else: cursor.checkpointToken()
  let nextPage = if response.body.len == 0: none(int) else: some(page + 1)

  FetchResult(
    body: response.body,
    fetchedAt: getTime().utc,
    statusCode: statusCode,
    contentType: (if response.headers.hasKey("Content-Type"): response.headers["Content-Type"] else: "application/json"),
    requestUrl: requestUrl,
    checkpointToken: checkpoint,
    nextPage: nextPage
  )

proc archiveRawCapture*(archiveRoot: string, cursor: SyncCursor, fetchResult: FetchResult): RawCapture =
  let fetchStamp = fetchResult.fetchedAt.format("yyyy/MM/dd/HHmmss'Z'")
  let captureDir = archiveRoot / SourceName / cursor.owner / cursor.repo / fetchStamp
  let page = max(cursor.page, 1)
  let rawPath = captureDir / fmt"page-{page}.json"
  let metadataPath = captureDir / fmt"page-{page}.metadata.json"

  createDir(captureDir)
  writeFile(rawPath, fetchResult.body)

  result = RawCapture(
    sourceName: SourceName,
    owner: cursor.owner,
    repo: cursor.repo,
    fetchedAt: fetchResult.fetchedAt.format("yyyy-MM-dd'T'HH:mm:ss'Z'"),
    rawPath: rawPath,
    metadataPath: metadataPath,
    sha256: $hash(fetchResult.body),
    checkpointToken: fetchResult.checkpointToken,
    requestUrl: fetchResult.requestUrl
  )

  writeFile(
    metadataPath,
    $(%*{
      "sourceName": result.sourceName,
      "owner": result.owner,
      "repo": result.repo,
      "fetchedAt": result.fetchedAt,
      "rawPath": result.rawPath,
      "metadataPath": result.metadataPath,
      "sha256": result.sha256,
      "checkpointToken": result.checkpointToken,
      "requestUrl": result.requestUrl,
    })
  )

proc parseArchivedReleasePayload*(rawCapture: RawCapture): seq[JsonNode] =
  let payload = parseFile(rawCapture.rawPath)
  for item in payload.items:
    if item.kind == JObject:
      result.add(item)

proc readString(node: JsonNode, key: string): string =
  if node.hasKey(key):
    node[key].getStr()
  else:
    ""

proc readInt(node: JsonNode, key: string): int =
  if node.hasKey(key):
    node[key].getInt()
  else:
    0

proc readBool(node: JsonNode, key: string): bool =
  node.hasKey(key) and node[key].getBool()

proc normalizeReleaseRecords*(rawCapture: RawCapture, payload: seq[JsonNode]): seq[NormalizedReleaseRecord] =
  let provenance = ReleaseProvenance(
    sourceName: rawCapture.sourceName,
    rawPath: rawCapture.rawPath,
    fetchedAt: rawCapture.fetchedAt,
    sha256: rawCapture.sha256,
    checkpointToken: rawCapture.checkpointToken,
    adapterVersion: AdapterVersion
  )

  for item in payload:
    if readBool(item, "draft"):
      continue

    let externalSlug = readString(item, "tag_name")
    let title = if readString(item, "name").len > 0: readString(item, "name") else: externalSlug

    result.add(
      NormalizedReleaseRecord(
        canonicalId: fmt"{SourceName}:{rawCapture.owner}/{rawCapture.repo}:{readInt(item, "id")}",
        sourceId: readInt(item, "id"),
        owner: rawCapture.owner,
        repo: rawCapture.repo,
        externalSlug: externalSlug,
        title: title,
        publishedAt: readString(item, "published_at"),
        canonicalUrl: readString(item, "html_url"),
        provenance: provenance
      )
    )

proc syncReleasePage*(service: GitHubReleaseSyncService, cursor: SyncCursor): SyncResult =
  let attempts = max(cursor.maxAttempts, 1)
  var fetchResult: FetchResult
  var fetched = false
  var lastError = ""

  for _ in 1 .. attempts:
    try:
      fetchResult = service.adapter.fetchReleasePage(cursor)
      fetched = true
      break
    except RetryableFetchError as exc:
      lastError = exc.msg

  if not fetched:
    raise newException(RetryableFetchError, lastError)

  let rawCapture = archiveRawCapture(service.archiveRoot, cursor, fetchResult)
  let payload = parseArchivedReleasePayload(rawCapture)
  let records = normalizeReleaseRecords(rawCapture, payload)

  result = SyncResult(
    rawCapture: rawCapture,
    records: records,
    nextCursor: if fetchResult.nextPage.isSome:
      some(
        SyncCursor(
          owner: cursor.owner,
          repo: cursor.repo,
          page: fetchResult.nextPage.get(),
          etag: some(fetchResult.checkpointToken),
          maxAttempts: cursor.maxAttempts
        )
      )
    else:
      none(SyncCursor)
  )

proc replayFromArchive*(service: GitHubReleaseSyncService, rawCapture: RawCapture): seq[NormalizedReleaseRecord] =
  discard service
  normalizeReleaseRecords(rawCapture, parseArchivedReleasePayload(rawCapture))

routes:
  post "/sources/github-releases/@owner/@repo/sync":
    let service = GitHubReleaseSyncService(
      adapter: SourceAdapter(client: newHttpClient()),
      archiveRoot: "./data/raw"
    )
    defer:
      service.adapter.client.close()

    let result = service.syncReleasePage(
      SyncCursor(
        owner: @"owner",
        repo: @"repo",
        page: 1,
        etag: none(string),
        maxAttempts: 2
      )
    )

    resp Http202, $(%*{
      "sourceName": SourceName,
      "rawPath": result.rawCapture.rawPath,
      "normalizedCount": result.records.len,
      "checkpointToken": result.rawCapture.checkpointToken,
      "nextPage": if result.nextCursor.isSome: result.nextCursor.get().page else: 0,
    })
