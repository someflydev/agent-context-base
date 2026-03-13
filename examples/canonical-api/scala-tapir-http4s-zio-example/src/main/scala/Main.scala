import cats.syntax.all.*
import com.comcast.ip4s.*
import org.http4s.HttpApp
import org.http4s.ember.server.EmberServerBuilder
import sttp.tapir.generic.auto.*
import sttp.tapir.json.zio.*
import sttp.tapir.server.http4s.Http4sServerInterpreter
import sttp.tapir.*
import zio.*
import zio.interop.catz.*
import zio.json.*

object Main extends ZIOAppDefault:
  final case class HealthSnapshot(status: String, service: String)
  object HealthSnapshot:
    given JsonCodec[HealthSnapshot] = DeriveJsonCodec.gen

  final case class ReportSummary(reportId: String, totalEvents: Int, status: String)
  object ReportSummary:
    given JsonCodec[ReportSummary] = DeriveJsonCodec.gen

  final case class ReportEnvelope(service: String, tenantId: String, reports: List[ReportSummary])
  object ReportEnvelope:
    given JsonCodec[ReportEnvelope] = DeriveJsonCodec.gen

  final case class SeriesPoint(x: String, y: Int)
  object SeriesPoint:
    given JsonCodec[SeriesPoint] = DeriveJsonCodec.gen

  final case class MetricSeries(name: String, points: List[SeriesPoint])
  object MetricSeries:
    given JsonCodec[MetricSeries] = DeriveJsonCodec.gen

  final case class ChartPayload(metric: String, series: List[MetricSeries])
  object ChartPayload:
    given JsonCodec[ChartPayload] = DeriveJsonCodec.gen

  private val healthEndpoint =
    endpoint.get
      .in("healthz")
      .out(jsonBody[HealthSnapshot])

  private val reportEndpoint =
    endpoint.get
      .in("api" / "reports" / path[String]("tenantId"))
      .out(jsonBody[ReportEnvelope])

  private val chartEndpoint =
    endpoint.get
      .in("data" / "chart" / path[String]("metric"))
      .out(jsonBody[ChartPayload])

  private val fragmentEndpoint =
    endpoint.get
      .in("fragments" / "report-card" / path[String]("tenantId"))
      .out(stringBody)

  private val healthRoutes =
    Http4sServerInterpreter[Task]().toRoutes(
      healthEndpoint.serverLogicSuccess[Task](_ =>
        ZIO.succeed(HealthSnapshot(status = "ok", service = "scala-tapir-http4s-zio-example"))
      )
    )

  private val apiRoutes =
    Http4sServerInterpreter[Task]().toRoutes(
      reportEndpoint.serverLogicSuccess[Task](tenantId =>
        ZIO.succeed(
          ReportEnvelope(
            service = "scala-tapir-http4s-zio-example",
            tenantId = tenantId,
            reports = List(
              ReportSummary(reportId = "daily-signups", totalEvents = 42, status = "ready")
            ),
          )
        )
      )
    )

  private def buildChartPayload(metric: String): ChartPayload =
    ChartPayload(
      metric = metric,
      series = List(
        MetricSeries(
          name = metric,
          points = List(
            SeriesPoint("2026-03-01", 18),
            SeriesPoint("2026-03-02", 24),
            SeriesPoint("2026-03-03", 31),
          ),
        )
      ),
    )

  private val dataRoutes =
    Http4sServerInterpreter[Task]().toRoutes(
      chartEndpoint.serverLogicSuccess[Task](metric => ZIO.succeed(buildChartPayload(metric)))
    )

  private def renderReportCard(tenantId: String, totalEvents: Int): String =
    s"""
       |<section id="report-card-$tenantId" class="report-card" hx-swap-oob="true">
       |  <strong>Tenant $tenantId</strong>
       |  <span>$totalEvents events in the last hour</span>
       |</section>
       |""".stripMargin.trim

  private val fragmentRoutes =
    Http4sServerInterpreter[Task]().toRoutes(
      fragmentEndpoint.serverLogicSuccess[Task](tenantId => ZIO.succeed(renderReportCard(tenantId, 42)))
    )

  private val httpApp: HttpApp[Task] =
    (healthRoutes <+> apiRoutes <+> dataRoutes <+> fragmentRoutes).orNotFound

  override val run: ZIO[Any, Throwable, Unit] =
    EmberServerBuilder
      .default[Task]
      .withHost(ipv4"0.0.0.0")
      .withPort(port"8080")
      .withHttpApp(httpApp)
      .build
      .useForever
