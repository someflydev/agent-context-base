package dev.tenantcore.auth.routes

import org.http4k.core.Body
import org.http4k.core.HttpHandler
import org.http4k.core.Response
import org.http4k.core.Status
import org.http4k.format.Jackson.auto

data class HealthResponse(val status: String)

class HealthRoutes {
    private val lens = Body.auto<HealthResponse>().toLens()

    fun handler(): HttpHandler = {
        lens(HealthResponse("ok"), Response(Status.OK))
    }
}
