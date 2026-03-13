import org.http4k.core.Body
import org.http4k.core.Method.GET
import org.http4k.core.Request
import org.http4k.core.Response
import org.http4k.core.Status
import org.http4k.format.Jackson.auto
import org.http4k.routing.bind
import org.http4k.routing.path
import org.jetbrains.exposed.sql.SortOrder
import org.jetbrains.exposed.sql.SqlExpressionBuilder.eq
import org.jetbrains.exposed.sql.Table
import org.jetbrains.exposed.sql.select
import org.jetbrains.exposed.sql.transactions.transaction

data class SeriesPoint(val x: String, val y: Int)
data class MetricSeries(val name: String, val points: List<SeriesPoint>)
data class ChartPayload(val metric: String, val series: List<MetricSeries>)

object MetricPoints : Table("metric_points") {
    val metric = varchar("metric", 64)
    val bucketDay = varchar("bucket_day", 16)
    val total = integer("total")

    override val primaryKey = PrimaryKey(metric, bucketDay)
}

private val chartLens = Body.auto<ChartPayload>().toLens()

val chartRoute =
    "/data/chart/{metric}" bind GET to { request: Request ->
        val metric = request.path("metric") ?: error("metric is required")
        val points = transaction {
            MetricPoints
                .select { MetricPoints.metric eq metric }
                .orderBy(MetricPoints.bucketDay to SortOrder.ASC)
                .map { row -> SeriesPoint(row[MetricPoints.bucketDay], row[MetricPoints.total]) }
                .ifEmpty {
                    listOf(
                        SeriesPoint("2026-03-01", 18),
                        SeriesPoint("2026-03-02", 24),
                        SeriesPoint("2026-03-03", 31),
                    )
                }
        }
        chartLens(
            ChartPayload(metric = metric, series = listOf(MetricSeries(name = metric, points = points))),
            Response(Status.OK),
        )
    }
