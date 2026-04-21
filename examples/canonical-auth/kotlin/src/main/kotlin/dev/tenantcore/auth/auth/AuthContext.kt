package dev.tenantcore.auth.auth

import org.http4k.core.Request
import org.http4k.core.RequestContexts
import org.http4k.core.with
import org.http4k.lens.RequestContextKey
import java.time.Instant

data class AuthContext(
    val sub: String,
    val email: String,
    val tenantId: String?,
    val tenantRole: String,
    val groups: List<String>,
    val permissions: List<String>,
    val aclVer: Int,
    val issuedAt: Instant,
    val expiresAt: Instant,
) {
    fun hasPermission(permission: String): Boolean = permissions.contains(permission)
}

val requestContexts = RequestContexts()

private val authContextKey = RequestContextKey.required<AuthContext>(requestContexts)

val Request.authContext: AuthContext
    get() = authContextKey(this)

fun Request.withAuthContext(authContext: AuthContext): Request = with(authContextKey of authContext)
