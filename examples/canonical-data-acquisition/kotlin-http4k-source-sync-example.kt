import com.fasterxml.jackson.module.kotlin.jacksonObjectMapper
import org.http4k.core.Body
import org.http4k.core.Method.GET
import org.http4k.core.Method.POST
import org.http4k.core.Request
import org.http4k.core.Response
import org.http4k.core.Status
import org.http4k.format.Jackson.auto
import org.http4k.lens.Query
import org.http4k.routing.bind
import org.http4k.routing.routes
import org.http4k.routing.path
import org.jetbrains.exposed.sql.SqlExpressionBuilder.eq
import org.jetbrains.exposed.sql.Table
import org.jetbrains.exposed.sql.insert
import org.jetbrains.exposed.sql.insertIgnore
import org.jetbrains.exposed.sql.select
import org.jetbrains.exposed.sql.transactions.transaction
import java.nio.file.Files
import java.nio.file.Path
import java.security.MessageDigest
import java.time.Instant

data class SyncCursor(
    val owner: String,
    val repo: String,
    val page: Int = 1,
    val etag: String? = null,
) {
    val checkpointToken: String
        get() = etag ?: "page=$page"
}

data class FetchResult(
    val body: String,
    val fetchedAt: Instant,
    val requestUrl: String,
    val checkpointToken: String,
    val nextPage: Int?,
)

data class RawCapture(
    val sourceName: String,
    val owner: String,
    val repo: String,
    val rawPath: String,
    val metadataPath: String,
    val fetchedAt: String,
    val sha256: String,
    val checkpointToken: String,
    val requestUrl: String,
)

data class ReleaseProvenance(
    val sourceName: String,
    val rawPath: String,
    val fetchedAt: String,
    val sha256: String,
    val checkpointToken: String,
    val adapterVersion: String,
)

data class SourceReleaseDto(
    val id: Long,
    val tag_name: String,
    val name: String?,
    val html_url: String,
    val published_at: String,
    val draft: Boolean = false,
)

data class NormalizedReleaseRecord(
    val canonicalId: String,
    val sourceId: Long,
    val owner: String,
    val repo: String,
    val tagName: String,
    val title: String,
    val publishedAt: String,
    val htmlUrl: String,
    val provenance: ReleaseProvenance,
)

data class SyncReceipt(
    val sourceName: String,
    val rawPath: String,
    val normalizedCount: Int,
    val checkpointToken: String,
    val nextCursor: SyncCursor?,
)

object SourceCheckpoints : Table("source_checkpoints") {
    val sourceName = varchar("source_name", 64)
    val owner = varchar("owner", 128)
    val repo = varchar("repo", 128)
    val page = integer("page")
    val checkpointToken = varchar("checkpoint_token", 128)

    override val primaryKey = PrimaryKey(sourceName, owner, repo)
}

object NormalizedReleases : Table("normalized_releases") {
    val canonicalId = varchar("canonical_id", 256)
    val sourceId = long("source_id")
    val owner = varchar("owner", 128)
    val repo = varchar("repo", 128)
    val tagName = varchar("tag_name", 128)
    val title = varchar("title", 256)
    val publishedAt = varchar("published_at", 64)
    val htmlUrl = varchar("html_url", 512)
    val provenanceJson = text("provenance_json")

    override val primaryKey = PrimaryKey(canonicalId)
}

interface ReleaseSourceClient {
    fun fetchReleasePage(cursor: SyncCursor): FetchResult
}

class SourceCheckpointRepository {
    fun load(owner: String, repo: String): SyncCursor? = transaction {
        SourceCheckpoints
            .select {
                (SourceCheckpoints.sourceName eq SOURCE_NAME) and
                    (SourceCheckpoints.owner eq owner) and
                    (SourceCheckpoints.repo eq repo)
            }
            .singleOrNull()
            ?.let { row ->
                SyncCursor(
                    owner = row[SourceCheckpoints.owner],
                    repo = row[SourceCheckpoints.repo],
                    page = row[SourceCheckpoints.page],
                    etag = row[SourceCheckpoints.checkpointToken],
                )
            }
    }

    fun save(cursor: SyncCursor) {
        transaction {
            SourceCheckpoints.insertIgnore {
                it[sourceName] = SOURCE_NAME
                it[owner] = cursor.owner
                it[repo] = cursor.repo
                it[page] = cursor.page
                it[checkpointToken] = cursor.checkpointToken
            }
        }
    }
}

class ReleaseRepository {
    private val mapper = jacksonObjectMapper()

    fun upsert(records: List<NormalizedReleaseRecord>) {
        transaction {
            records.forEach { record ->
                NormalizedReleases.insertIgnore {
                    it[canonicalId] = record.canonicalId
                    it[sourceId] = record.sourceId
                    it[owner] = record.owner
                    it[repo] = record.repo
                    it[tagName] = record.tagName
                    it[title] = record.title
                    it[publishedAt] = record.publishedAt
                    it[htmlUrl] = record.htmlUrl
                    it[provenanceJson] = mapper.writeValueAsString(record.provenance)
                }
            }
        }
    }
}

class FileArchive(private val archiveRoot: Path) {
    private val mapper = jacksonObjectMapper()

    fun archiveRawCapture(cursor: SyncCursor, fetchResult: FetchResult): RawCapture {
        val captureDir = archiveRoot
            .resolve(SOURCE_NAME)
            .resolve(cursor.owner)
            .resolve(cursor.repo)
            .resolve(fetchResult.fetchedAt.toString().replace(":", ""))
        Files.createDirectories(captureDir)

        val rawPath = captureDir.resolve("page-${cursor.page}.json")
        val metadataPath = captureDir.resolve("page-${cursor.page}.metadata.json")
        Files.writeString(rawPath, fetchResult.body)

        val rawCapture = RawCapture(
            sourceName = SOURCE_NAME,
            owner = cursor.owner,
            repo = cursor.repo,
            rawPath = rawPath.toString(),
            metadataPath = metadataPath.toString(),
            fetchedAt = fetchResult.fetchedAt.toString(),
            sha256 = sha256(fetchResult.body),
            checkpointToken = fetchResult.checkpointToken,
            requestUrl = fetchResult.requestUrl,
        )
        Files.writeString(metadataPath, mapper.writeValueAsString(rawCapture))
        return rawCapture
    }

    fun parseArchivedReleasePayload(rawCapture: RawCapture): List<SourceReleaseDto> =
        mapper.readValue(Files.readString(Path.of(rawCapture.rawPath)), mapper.typeFactory.constructCollectionType(List::class.java, SourceReleaseDto::class.java))
}

class GitHubReleaseSyncService(
    private val sourceClient: ReleaseSourceClient,
    private val archive: FileArchive,
    private val checkpoints: SourceCheckpointRepository,
    private val releases: ReleaseRepository,
) {
    fun syncReleasePage(owner: String, repo: String, requestedPage: Int?): SyncReceipt {
        val storedCursor = checkpoints.load(owner, repo)
        val cursor = storedCursor?.copy(page = requestedPage ?: storedCursor.page)
            ?: SyncCursor(owner = owner, repo = repo, page = requestedPage ?: 1)
        val fetchResult = sourceClient.fetchReleasePage(cursor)
        val rawCapture = archive.archiveRawCapture(cursor, fetchResult)
        val records = replayFromArchive(rawCapture)
        val nextCursor = fetchResult.nextPage?.let { page ->
            SyncCursor(owner = owner, repo = repo, page = page, etag = fetchResult.checkpointToken)
        }

        releases.upsert(records)
        nextCursor?.let(checkpoints::save)

        return SyncReceipt(
            sourceName = rawCapture.sourceName,
            rawPath = rawCapture.rawPath,
            normalizedCount = records.size,
            checkpointToken = rawCapture.checkpointToken,
            nextCursor = nextCursor,
        )
    }

    fun replayFromArchive(rawCapture: RawCapture): List<NormalizedReleaseRecord> {
        val provenance = ReleaseProvenance(
            sourceName = rawCapture.sourceName,
            rawPath = rawCapture.rawPath,
            fetchedAt = rawCapture.fetchedAt,
            sha256 = rawCapture.sha256,
            checkpointToken = rawCapture.checkpointToken,
            adapterVersion = ADAPTER_VERSION,
        )
        return archive
            .parseArchivedReleasePayload(rawCapture)
            .filterNot { it.draft }
            .sortedByDescending { it.published_at }
            .map { dto ->
                NormalizedReleaseRecord(
                    canonicalId = "${rawCapture.sourceName}:${rawCapture.owner}/${rawCapture.repo}:${dto.id}",
                    sourceId = dto.id,
                    owner = rawCapture.owner,
                    repo = rawCapture.repo,
                    tagName = dto.tag_name,
                    title = dto.name ?: dto.tag_name,
                    publishedAt = dto.published_at,
                    htmlUrl = dto.html_url,
                    provenance = provenance,
                )
            }
    }
}

private val mapper = jacksonObjectMapper()
private val receiptLens = Body.auto<SyncReceipt>().toLens()
private val replayLens = Body.auto<List<NormalizedReleaseRecord>>().toLens()
private val pageQuery = Query.int().optional("page")

const val SOURCE_NAME = "github-releases"
const val ADAPTER_VERSION = "github-releases-v1"

fun sourceSyncRoutes(service: GitHubReleaseSyncService) = routes(
    "/source-sync/{owner}/{repo}" bind POST to { request: Request ->
        val owner = request.path("owner") ?: error("owner is required")
        val repo = request.path("repo") ?: error("repo is required")
        val receipt = service.syncReleasePage(owner, repo, pageQuery(request))
        receiptLens(receipt, Response(Status.ACCEPTED))
    },
    "/source-sync/replay" bind GET to { request: Request ->
        val rawPath = request.query("rawPath") ?: error("rawPath is required")
        val metadata = mapper.readValue(Files.readString(Path.of("$rawPath.metadata.json")), RawCapture::class.java)
        replayLens(service.replayFromArchive(metadata), Response(Status.OK))
    },
)

private fun sha256(body: String): String =
    MessageDigest.getInstance("SHA-256")
        .digest(body.toByteArray())
        .joinToString("") { "%02x".format(it) }
