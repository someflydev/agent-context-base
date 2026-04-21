package dev.tenantcore.auth.routes

import dev.tenantcore.auth.auth.authContext
import dev.tenantcore.auth.domain.InMemoryStore
import dev.tenantcore.auth.registry.getAllowedRoutes
import dev.tenantcore.auth.registry.getGuideSections
import org.http4k.core.Body
import org.http4k.core.HttpHandler
import org.http4k.core.Response
import org.http4k.core.Status
import org.http4k.format.Jackson.auto

data class AllowedRouteView(
    val method: String,
    val path: String,
    val permission: String,
    val description: String,
    val service: String,
    val resource: String,
    val action: String,
)

data class MeResponse(
    val sub: String,
    val email: String,
    val display_name: String,
    val tenant_id: String?,
    val tenant_name: String?,
    val tenant_role: String,
    val groups: List<String>,
    val permissions: List<String>,
    val acl_ver: Int,
    val allowed_routes: List<AllowedRouteView>,
    val guide_sections: List<String>,
    val issued_at: String,
    val expires_at: String,
)

class MeRoutes {
    private val responseLens = Body.auto<MeResponse>().toLens()

    fun handler(store: InMemoryStore): HttpHandler = { request ->
        val auth = request.authContext
        val user = store.getUserById(auth.sub) ?: error("Missing user ${auth.sub}")
        val response = MeResponse(
            sub = auth.sub,
            email = auth.email,
            display_name = user.displayName,
            tenant_id = auth.tenantId,
            tenant_name = auth.tenantId?.let(store::getTenantName),
            tenant_role = auth.tenantRole,
            groups = auth.groups,
            permissions = auth.permissions,
            acl_ver = auth.aclVer,
            allowed_routes = getAllowedRoutes(auth).map {
                AllowedRouteView(
                    method = it.method,
                    path = it.path,
                    permission = it.permission ?: "",
                    description = it.description,
                    service = it.service,
                    resource = it.resource,
                    action = it.action,
                )
            },
            guide_sections = getGuideSections(auth),
            issued_at = auth.issuedAt.toString(),
            expires_at = auth.expiresAt.toString(),
        )
        responseLens(response, Response(Status.OK))
    }
}
