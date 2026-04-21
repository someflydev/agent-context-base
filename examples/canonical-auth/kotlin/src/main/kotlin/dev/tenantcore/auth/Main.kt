package dev.tenantcore.auth

import dev.tenantcore.auth.auth.TokenService
import dev.tenantcore.auth.auth.jwtMiddleware
import dev.tenantcore.auth.auth.requestContexts
import dev.tenantcore.auth.auth.requirePermission
import dev.tenantcore.auth.auth.requireSuperAdmin
import dev.tenantcore.auth.domain.InMemoryStore
import dev.tenantcore.auth.routes.AdminRoutes
import dev.tenantcore.auth.routes.AuthRoutes
import dev.tenantcore.auth.routes.GroupRoutes
import dev.tenantcore.auth.routes.HealthRoutes
import dev.tenantcore.auth.routes.MeRoutes
import dev.tenantcore.auth.routes.PermissionRoutes
import dev.tenantcore.auth.routes.UserRoutes
import org.http4k.core.HttpHandler
import org.http4k.core.Method.GET
import org.http4k.core.Method.PATCH
import org.http4k.core.Method.POST
import org.http4k.core.then
import org.http4k.filter.ServerFilters
import org.http4k.routing.bind
import org.http4k.routing.routes
import org.http4k.server.Jetty
import org.http4k.server.asServer
import java.nio.file.Path

fun app(
    store: InMemoryStore = InMemoryStore.loadFromFixtures(Path.of("..", "domain", "fixtures")),
    tokenService: TokenService = TokenService(),
): HttpHandler {
    val authRoutes = AuthRoutes()
    val meRoutes = MeRoutes()
    val userRoutes = UserRoutes()
    val groupRoutes = GroupRoutes()
    val adminRoutes = AdminRoutes()
    val permissionRoutes = PermissionRoutes()
    val healthRoutes = HealthRoutes()

    val tenantProtected = routes(
        "/me" bind GET to meRoutes.handler(store),
        "/users" bind GET to (requirePermission("iam:user:read").then(userRoutes.listHandler(store))),
        "/users" bind POST to (requirePermission("iam:user:invite").then(userRoutes.inviteHandler(store))),
        "/users/{id}" bind GET to (requirePermission("iam:user:read").then(userRoutes.getHandler(store))),
        "/users/{id}" bind PATCH to (requirePermission("iam:user:update").then(userRoutes.patchHandler(store))),
        "/groups" bind GET to (requirePermission("iam:group:read").then(groupRoutes.listHandler(store))),
        "/groups" bind POST to (requirePermission("iam:group:create").then(groupRoutes.createHandler(store))),
        "/groups/{id}/permissions" bind POST to (requirePermission("iam:group:assign_permission").then(groupRoutes.assignPermissionHandler(store))),
        "/groups/{id}/users" bind POST to (requirePermission("iam:group:assign_user").then(groupRoutes.assignUserHandler(store))),
        "/permissions" bind GET to (requirePermission("iam:permission:read").then(permissionRoutes.listHandler(store))),
    )

    val superAdminProtected = routes(
        "/admin/tenants" bind GET to adminRoutes.listTenantsHandler(store),
        "/admin/tenants" bind POST to adminRoutes.createTenantHandler(store),
    )

    return ServerFilters.InitialiseRequestContext(requestContexts).then(
        routes(
            "/health" bind GET to healthRoutes.handler(),
            "/auth/token" bind POST to authRoutes.tokenHandler(store, tokenService),
            jwtMiddleware(store, tokenService).then(tenantProtected),
            jwtMiddleware(store, tokenService).then(requireSuperAdmin().then(superAdminProtected)),
        ),
    )
}

fun main() {
    app().asServer(Jetty(8080)).start()
    Thread.currentThread().join()
}
