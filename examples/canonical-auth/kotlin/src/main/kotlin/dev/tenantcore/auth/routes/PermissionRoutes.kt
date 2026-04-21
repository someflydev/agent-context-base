package dev.tenantcore.auth.routes

import dev.tenantcore.auth.domain.InMemoryStore
import dev.tenantcore.auth.domain.Permission
import org.http4k.core.Body
import org.http4k.core.HttpHandler
import org.http4k.core.Response
import org.http4k.core.Status
import org.http4k.format.Jackson.auto

class PermissionRoutes {
    private val permissionsLens = Body.auto<List<Permission>>().toLens()

    fun listHandler(store: InMemoryStore): HttpHandler = {
        permissionsLens(store.getAllPermissions(), Response(Status.OK))
    }
}
