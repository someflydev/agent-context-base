package example

import org.http4k.core.Body
import org.http4k.core.HttpHandler
import org.http4k.core.Method.GET
import org.http4k.core.Response
import org.http4k.core.Status
import org.http4k.format.Jackson.auto
import org.http4k.routing.bind
import org.http4k.routing.path
import org.http4k.routing.routes
import org.http4k.server.Jetty
import org.http4k.server.asServer
import org.jetbrains.exposed.sql.Database
import org.jetbrains.exposed.sql.SchemaUtils
import org.jetbrains.exposed.sql.SortOrder
import org.jetbrains.exposed.sql.SqlExpressionBuilder.eq
import org.jetbrains.exposed.sql.Table
import org.jetbrains.exposed.sql.insert
import org.jetbrains.exposed.sql.select
import org.jetbrains.exposed.sql.selectAll
import org.jetbrains.exposed.sql.transactions.transaction

private const val SERVICE_NAME = "kotlin-http4k-exposed-example"

data class HealthSnapshot(val status: String, val service: String)
data class ReportSummary(val reportId: String, val totalEvents: Int, val status: String)
data class ReportEnvelope(val service: String, val tenantId: String, val reports: List<ReportSummary>)
data class SeriesPoint(val x: String, val y: Int)
data class MetricSeries(val name: String, val points: List<SeriesPoint>)
data class ChartPayload(val metric: String, val series: List<MetricSeries>)

object Reports : Table("reports") {
    val tenantId = varchar("tenant_id", 64)
    val reportId = varchar("report_id", 64)
    val totalEvents = integer("total_events")
    val status = varchar("status", 32)

    override val primaryKey = PrimaryKey(tenantId, reportId)
}

object MetricPoints : Table("metric_points") {
    val metric = varchar("metric", 64)
    val bucketDay = varchar("bucket_day", 16)
    val total = integer("total")

    override val primaryKey = PrimaryKey(metric, bucketDay)
}

private val healthLens = Body.auto<HealthSnapshot>().toLens()
private val reportLens = Body.auto<ReportEnvelope>().toLens()
private val chartLens = Body.auto<ChartPayload>().toLens()

private fun connectDatabase() {
    Database.connect(
        url = "jdbc:h2:mem:http4k;DB_CLOSE_DELAY=-1;MODE=PostgreSQL",
        driver = "org.h2.Driver",
    )
    transaction {
        SchemaUtils.create(Reports, MetricPoints)
        if (Reports.selectAll().count() == 0L) {
            Reports.insert {
                it[Reports.tenantId] = "acme"
                it[Reports.reportId] = "daily-signups"
                it[Reports.totalEvents] = 42
                it[Reports.status] = "ready"
            }
        }
        if (MetricPoints.selectAll().count() == 0L) {
            listOf(
                "2026-03-01" to 18,
                "2026-03-02" to 24,
                "2026-03-03" to 31,
            ).forEach { (bucketDay, total) ->
                MetricPoints.insert {
                    it[MetricPoints.metric] = "signups"
                    it[MetricPoints.bucketDay] = bucketDay
                    it[MetricPoints.total] = total
                }
            }
        }
    }
}

private fun fetchReport(tenantId: String): ReportSummary =
    transaction {
        Reports
            .select { Reports.tenantId eq tenantId }
            .limit(1)
            .map { row ->
                ReportSummary(
                    reportId = row[Reports.reportId],
                    totalEvents = row[Reports.totalEvents],
                    status = row[Reports.status],
                )
            }
            .singleOrNull()
            ?: ReportSummary("daily-signups", 42, "ready")
    }

private fun fetchSeries(metric: String): List<SeriesPoint> =
    transaction {
        MetricPoints
            .select { MetricPoints.metric eq metric }
            .orderBy(MetricPoints.bucketDay to SortOrder.ASC)
            .map { row -> SeriesPoint(x = row[MetricPoints.bucketDay], y = row[MetricPoints.total]) }
            .ifEmpty {
                listOf(
                    SeriesPoint("2026-03-01", 18),
                    SeriesPoint("2026-03-02", 24),
                    SeriesPoint("2026-03-03", 31),
                )
            }
    }

private fun renderReportCard(tenantId: String, totalEvents: Int): String =
    """
    <section id="report-card-$tenantId" class="report-card" hx-swap-oob="true">
      <strong>Tenant $tenantId</strong>
      <span>$totalEvents events in the last hour</span>
    </section>
    """.trimIndent()

private val app: HttpHandler =
    routes(
        "/healthz" bind GET to {
            healthLens(HealthSnapshot(status = "ok", service = SERVICE_NAME), Response(Status.OK))
        },
        "/api/reports/{tenantId}" bind GET to { request ->
            val tenantId = request.path("tenantId") ?: error("tenantId is required")
            reportLens(
                ReportEnvelope(
                    service = SERVICE_NAME,
                    tenantId = tenantId,
                    reports = listOf(fetchReport(tenantId)),
                ),
                Response(Status.OK),
            )
        },
        "/fragments/report-card/{tenantId}" bind GET to { request ->
            val tenantId = request.path("tenantId") ?: error("tenantId is required")
            val report = fetchReport(tenantId)
            Response(Status.OK)
                .header("content-type", "text/html; charset=utf-8")
                .body(renderReportCard(tenantId, report.totalEvents))
        },
        "/data/chart/{metric}" bind GET to { request ->
            val metric = request.path("metric") ?: error("metric is required")
            chartLens(
                ChartPayload(
                    metric = metric,
                    series = listOf(MetricSeries(name = metric, points = fetchSeries(metric))),
                ),
                Response(Status.OK),
            )
        },
    )

fun main() {
    connectDatabase()
    app.asServer(Jetty(8080)).start()
    Thread.currentThread().join()
}
