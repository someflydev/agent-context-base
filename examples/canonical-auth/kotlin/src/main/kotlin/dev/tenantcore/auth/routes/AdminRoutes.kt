package dev.tenantcore.auth.routes

import dev.tenantcore.auth.domain.InMemoryStore
import dev.tenantcore.auth.domain.Tenant
import org.http4k.core.Body
import org.http4k.core.HttpHandler
import org.http4k.core.Response
import org.http4k.core.Status
import org.http4k.format.Jackson.auto

data class CreateTenantRequest(val slug: String, val name: String, val first_admin_email: String)

class AdminRoutes {
    private val tenantsLens = Body.auto<List<Tenant>>().toLens()
    private val tenantLens = Body.auto<Tenant>().toLens()
    private val createLens = Body.auto<CreateTenantRequest>().toLens()

    fun listTenantsHandler(store: InMemoryStore): HttpHandler = {
        tenantsLens(store.getAllTenants(), Response(Status.OK))
    }

    fun createTenantHandler(store: InMemoryStore): HttpHandler = { request ->
        val payload = createLens(request)
        val tenant = store.createTenant(payload.slug, payload.name, payload.first_admin_email)
        tenantLens(tenant, Response(Status.CREATED))
    }
}
