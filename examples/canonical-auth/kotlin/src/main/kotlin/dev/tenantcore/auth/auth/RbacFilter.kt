package dev.tenantcore.auth.auth

import org.http4k.core.Filter
import org.http4k.core.Response
import org.http4k.core.Status

fun requirePermission(permission: String): Filter = Filter { next ->
    { request ->
        val auth = try {
            request.authContext
        } catch (_: Exception) {
            return@Filter Response(Status.UNAUTHORIZED)
        }
        if (!auth.hasPermission(permission)) {
            Response(Status.FORBIDDEN)
        } else {
            next(request)
        }
    }
}

fun requireSuperAdmin(): Filter = Filter { next ->
    { request ->
        val auth = try {
            request.authContext
        } catch (_: Exception) {
            return@Filter Response(Status.UNAUTHORIZED)
        }
        if (auth.tenantRole != "super_admin") {
            Response(Status.FORBIDDEN)
        } else {
            next(request)
        }
    }
}
