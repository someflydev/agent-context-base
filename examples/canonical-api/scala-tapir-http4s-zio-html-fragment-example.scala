import org.http4s.HttpRoutes
import org.http4s.MediaType
import org.http4s.dsl.Http4sDsl
import org.http4s.headers.`Content-Type`
import zio.Task

object HtmlFragmentEndpointExample:
  private object Dsl extends Http4sDsl[Task]
  import Dsl.*

  def renderReportCard(tenantId: String, totalEvents: Int): String =
    s"""
       |<section id="report-card-$tenantId" class="report-card" hx-swap-oob="true">
       |  <strong>Tenant $tenantId</strong>
       |  <span>$totalEvents events in the last hour</span>
       |</section>
       |""".stripMargin.trim

  val routes: HttpRoutes[Task] =
    HttpRoutes.of[Task] {
      case GET -> Root / "fragments" / "report-card" / tenantId =>
        Ok(renderReportCard(tenantId, 42))
          .map(_.withContentType(`Content-Type`(MediaType.text.html)))
    }
