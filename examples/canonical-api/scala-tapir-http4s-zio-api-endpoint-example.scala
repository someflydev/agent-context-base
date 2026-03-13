import org.http4s.HttpRoutes
import sttp.tapir.generic.auto.*
import sttp.tapir.json.zio.*
import sttp.tapir.server.http4s.Http4sServerInterpreter
import sttp.tapir.*
import zio.*
import zio.json.*

final case class ReportSummary(reportId: String, totalEvents: Int, status: String)
object ReportSummary:
  given JsonCodec[ReportSummary] = DeriveJsonCodec.gen

final case class ReportEnvelope(tenantId: String, reports: List[ReportSummary])
object ReportEnvelope:
  given JsonCodec[ReportEnvelope] = DeriveJsonCodec.gen

object TypedReportEndpointExample:
  val listReportsEndpoint =
    endpoint.get
      .in("api" / "tenants" / path[String]("tenantId") / "reports")
      .in(query[Option[Int]]("limit"))
      .out(jsonBody[ReportEnvelope])

  val routes: HttpRoutes[Task] =
    Http4sServerInterpreter[Task]().toRoutes(
      listReportsEndpoint.serverLogicSuccess[Task] { case (tenantId, limit) =>
        ZIO.succeed(
          ReportEnvelope(
            tenantId = tenantId,
            reports = List(
              ReportSummary(
                reportId = "daily-signups",
                totalEvents = limit.getOrElse(42),
                status = "ready",
              )
            ),
          )
        )
      }
    )
