import org.http4s.HttpRoutes
import sttp.tapir.generic.auto.*
import sttp.tapir.json.zio.*
import sttp.tapir.server.http4s.Http4sServerInterpreter
import sttp.tapir.*
import zio.*
import zio.json.*

final case class SeriesPoint(x: String, y: Int)
object SeriesPoint:
  given JsonCodec[SeriesPoint] = DeriveJsonCodec.gen

final case class MetricSeries(name: String, points: List[SeriesPoint])
object MetricSeries:
  given JsonCodec[MetricSeries] = DeriveJsonCodec.gen

final case class ChartPayload(metric: String, series: List[MetricSeries])
object ChartPayload:
  given JsonCodec[ChartPayload] = DeriveJsonCodec.gen

object ChartDataEndpointExample:
  val chartEndpoint =
    endpoint.get
      .in("data" / "chart" / path[String]("metric"))
      .out(jsonBody[ChartPayload])

  def buildPayload(metric: String): ChartPayload =
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

  val routes: HttpRoutes[Task] =
    Http4sServerInterpreter[Task]().toRoutes(
      chartEndpoint.serverLogicSuccess[Task](metric => ZIO.succeed(buildPayload(metric)))
    )
