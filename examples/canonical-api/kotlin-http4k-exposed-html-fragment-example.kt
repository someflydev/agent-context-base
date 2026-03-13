import org.http4k.core.Method.GET
import org.http4k.core.Response
import org.http4k.core.Status
import org.http4k.routing.bind
import org.http4k.routing.path

fun renderReportCard(tenantId: String, totalEvents: Int): String =
    """
    <section id="report-card-$tenantId" class="report-card" hx-swap-oob="true">
      <strong>Tenant $tenantId</strong>
      <span>$totalEvents events in the last hour</span>
    </section>
    """.trimIndent()

val fragmentRoute =
    "/fragments/report-card/{tenantId}" bind GET to { request ->
        val tenantId = request.path("tenantId") ?: error("tenantId is required")
        Response(Status.OK)
            .header("content-type", "text/html; charset=utf-8")
            .body(renderReportCard(tenantId, 42))
    }
