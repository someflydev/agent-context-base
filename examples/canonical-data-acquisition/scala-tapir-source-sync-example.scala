import java.nio.charset.StandardCharsets
import java.nio.file.Path
import java.security.MessageDigest
import java.time.Instant

import org.http4s.HttpRoutes
import sttp.tapir.*
import sttp.tapir.generic.auto.*
import sttp.tapir.json.zio.*
import sttp.tapir.server.http4s.Http4sServerInterpreter
import zio.*
import zio.json.*

final case class SyncCursor(
    owner: String,
    repo: String,
    page: Int = 1,
    etag: Option[String] = None,
):
  def checkpointToken: String = etag.getOrElse(s"page=$page")

object SyncCursor:
  given JsonCodec[SyncCursor] = DeriveJsonCodec.gen

final case class SyncRequest(
    owner: String,
    repo: String,
    page: Option[Int] = None,
    etag: Option[String] = None,
)

object SyncRequest:
  given JsonCodec[SyncRequest] = DeriveJsonCodec.gen

final case class SyncInvocation(
    owner: String,
    repo: String,
    page: Option[Int] = None,
    etag: Option[String] = None,
)

final case class FetchResult(
    body: String,
    fetchedAt: Instant,
    requestUrl: String,
    checkpointToken: String,
    nextPage: Option[Int],
)

final case class RawCapture(
    sourceName: String,
    owner: String,
    repo: String,
    rawPath: String,
    metadataPath: String,
    fetchedAt: Instant,
    sha256: String,
    checkpointToken: String,
    requestUrl: String,
)

object RawCapture:
  given JsonCodec[RawCapture] = DeriveJsonCodec.gen

final case class ReleaseDto(
    id: Long,
    tagName: String,
    name: Option[String],
    htmlUrl: String,
    publishedAt: String,
    draft: Boolean,
)

object ReleaseDto:
  given JsonCodec[ReleaseDto] = DeriveJsonCodec.gen

final case class ReleaseProvenance(
    sourceName: String,
    rawPath: String,
    fetchedAt: Instant,
    sha256: String,
    checkpointToken: String,
    adapterVersion: String,
)

object ReleaseProvenance:
  given JsonCodec[ReleaseProvenance] = DeriveJsonCodec.gen

final case class NormalizedReleaseRecord(
    canonicalId: String,
    sourceId: Long,
    owner: String,
    repo: String,
    tagName: String,
    title: String,
    publishedAt: String,
    htmlUrl: String,
    provenance: ReleaseProvenance,
)

object NormalizedReleaseRecord:
  given JsonCodec[NormalizedReleaseRecord] = DeriveJsonCodec.gen

final case class SyncReceipt(
    sourceName: String,
    rawPath: String,
    normalizedCount: Int,
    checkpointToken: String,
    nextCursor: Option[SyncCursor],
)

object SyncReceipt:
  given JsonCodec[SyncReceipt] = DeriveJsonCodec.gen

trait ReleaseSourceClient:
  def fetchReleasePage(cursor: SyncCursor): Task[FetchResult]

trait RawArchive:
  def archive(cursor: SyncCursor, fetchResult: FetchResult): Task[RawCapture]
  def readRaw(rawCapture: RawCapture): Task[String]

trait ReleaseRepository:
  def save(records: Chunk[NormalizedReleaseRecord], nextCursor: Option[SyncCursor]): Task[Unit]

final case class GitHubReleaseSyncService(
    client: ReleaseSourceClient,
    archive: RawArchive,
    repository: ReleaseRepository,
):
  private val SourceName = "github-releases"
  private val AdapterVersion = "github-releases-v1"

  private def checksum(body: String): String =
    MessageDigest
      .getInstance("SHA-256")
      .digest(body.getBytes(StandardCharsets.UTF_8))
      .map("%02x".format(_))
      .mkString

  def archiveRawCapture(cursor: SyncCursor, fetchResult: FetchResult): Task[RawCapture] =
    archive.archive(cursor, fetchResult).map { archived =>
      archived.copy(
        sourceName = SourceName,
        sha256 = if archived.sha256.nonEmpty then archived.sha256 else checksum(fetchResult.body),
        checkpointToken = fetchResult.checkpointToken,
        requestUrl = fetchResult.requestUrl,
      )
    }

  def parseArchivedReleasePayload(rawCapture: RawCapture): Task[Chunk[ReleaseDto]] =
    archive.readRaw(rawCapture).flatMap { body =>
      ZIO
        .fromEither(body.fromJson[Chunk[ReleaseDto]])
        .mapError(message => new IllegalArgumentException(message))
    }

  def normalizeReleaseDtos(
      rawCapture: RawCapture,
      payload: Chunk[ReleaseDto],
  ): Chunk[NormalizedReleaseRecord] =
    val provenance = ReleaseProvenance(
      sourceName = rawCapture.sourceName,
      rawPath = rawCapture.rawPath,
      fetchedAt = rawCapture.fetchedAt,
      sha256 = rawCapture.sha256,
      checkpointToken = rawCapture.checkpointToken,
      adapterVersion = AdapterVersion,
    )

    payload
      .filterNot(_.draft)
      .sortBy(_.publishedAt)(Ordering.String.reverse)
      .map { dto =>
        NormalizedReleaseRecord(
          canonicalId = s"${rawCapture.sourceName}:${rawCapture.owner}/${rawCapture.repo}:${dto.id}",
          sourceId = dto.id,
          owner = rawCapture.owner,
          repo = rawCapture.repo,
          tagName = dto.tagName,
          title = dto.name.getOrElse(dto.tagName),
          publishedAt = dto.publishedAt,
          htmlUrl = dto.htmlUrl,
          provenance = provenance,
        )
      }

  def replayFromArchive(rawCapture: RawCapture): Task[Chunk[NormalizedReleaseRecord]] =
    parseArchivedReleasePayload(rawCapture).map(normalizeReleaseDtos(rawCapture, _))

  def syncReleasePage(request: SyncRequest): Task[SyncReceipt] =
    val cursor = SyncCursor(
      owner = request.owner,
      repo = request.repo,
      page = request.page.getOrElse(1),
      etag = request.etag,
    )

    for
      fetchResult <- client.fetchReleasePage(cursor)
      rawCapture <- archiveRawCapture(cursor, fetchResult)
      records <- replayFromArchive(rawCapture)
      nextCursor = fetchResult.nextPage.map(nextPage =>
        cursor.copy(page = nextPage, etag = Some(fetchResult.checkpointToken))
      )
      _ <- repository.save(records, nextCursor)
    yield SyncReceipt(
      sourceName = rawCapture.sourceName,
      rawPath = rawCapture.rawPath,
      normalizedCount = records.length,
      checkpointToken = rawCapture.checkpointToken,
      nextCursor = nextCursor,
    )

object SourceSyncEndpointExample:
  val syncEndpoint =
    endpoint.post
      .in("source-sync")
      .in(path[String]("owner"))
      .in(path[String]("repo"))
      .in(query[Option[Int]]("page"))
      .in(query[Option[String]]("etag"))
      .mapInTo[SyncInvocation]
      .out(jsonBody[SyncReceipt])

  val replayEndpoint =
    endpoint.get
      .in("source-sync" / "replay")
      .in(query[String]("rawPath"))
      .out(jsonBody[List[NormalizedReleaseRecord]])

  def routes(service: GitHubReleaseSyncService): HttpRoutes[Task] =
    Http4sServerInterpreter[Task]().toRoutes(
      List(
        syncEndpoint.serverLogicSuccess[Task] { invocation =>
          service.syncReleasePage(
            SyncRequest(
              owner = invocation.owner,
              repo = invocation.repo,
              page = invocation.page,
              etag = invocation.etag,
            )
          )
        },
        replayEndpoint.serverLogicSuccess[Task](rawPath =>
          service
            .replayFromArchive(
              RawCapture(
                sourceName = "github-releases",
                owner = "replay",
                repo = "replay",
                rawPath = rawPath,
                metadataPath = s"$rawPath.metadata.json",
                fetchedAt = Instant.EPOCH,
                sha256 = "",
                checkpointToken = "replay",
                requestUrl = s"file://${Path.of(rawPath)}",
              )
            )
            .map(_.toList)
        ),
      )
    )
