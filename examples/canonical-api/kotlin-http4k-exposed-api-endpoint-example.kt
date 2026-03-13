import org.http4k.core.Body
import org.http4k.core.Method.GET
import org.http4k.core.Request
import org.http4k.core.Response
import org.http4k.core.Status
import org.http4k.format.Jackson.auto
import org.http4k.routing.bind
import org.http4k.routing.path
import org.jetbrains.exposed.sql.SqlExpressionBuilder.eq
import org.jetbrains.exposed.sql.Table
import org.jetbrains.exposed.sql.select
import org.jetbrains.exposed.sql.transactions.transaction

data class ReportSummary(val reportId: String, val totalEvents: Int, val status: String)
data class ReportEnvelope(val service: String, val tenantId: String, val reports: List<ReportSummary>)

object Reports : Table("reports") {
    val tenantId = varchar("tenant_id", 64)
    val reportId = varchar("report_id", 64)
    val totalEvents = integer("total_events")
    val status = varchar("status", 32)

    override val primaryKey = PrimaryKey(tenantId, reportId)
}

private val reportLens = Body.auto<ReportEnvelope>().toLens()

val reportRoute =
    "/api/reports/{tenantId}" bind GET to { request: Request ->
        val tenantId = request.path("tenantId") ?: error("tenantId is required")
        val payload = transaction {
            Reports
                .select { Reports.tenantId eq tenantId }
                .limit(1)
                .map { row ->
                    ReportEnvelope(
                        service = "kotlin-http4k-exposed",
                        tenantId = tenantId,
                        reports = listOf(
                            ReportSummary(
                                reportId = row[Reports.reportId],
                                totalEvents = row[Reports.totalEvents],
                                status = row[Reports.status],
                            )
                        ),
                    )
                }
                .singleOrNull()
                ?: ReportEnvelope(
                    service = "kotlin-http4k-exposed",
                    tenantId = tenantId,
                    reports = listOf(ReportSummary("daily-signups", 42, "ready")),
                )
        }
        reportLens(payload, Response(Status.OK))
    }
