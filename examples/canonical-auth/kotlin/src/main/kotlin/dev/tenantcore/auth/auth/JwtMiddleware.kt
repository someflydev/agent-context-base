package dev.tenantcore.auth.auth

import dev.tenantcore.auth.domain.InMemoryStore
import io.jsonwebtoken.Claims
import io.jsonwebtoken.JwtException
import org.http4k.core.Filter
import org.http4k.core.Response
import org.http4k.core.Status

fun jwtMiddleware(store: InMemoryStore, tokenService: TokenService): Filter = Filter { next ->
    { request ->
        val header = request.header("Authorization") ?: return@Filter Response(Status.UNAUTHORIZED)
        if (!header.startsWith("Bearer ")) {
            return@Filter Response(Status.UNAUTHORIZED)
        }
        val token = header.removePrefix("Bearer ").trim()
        val claims = try {
            tokenService.parseToken(token)
        } catch (_: JwtException) {
            return@Filter Response(Status.UNAUTHORIZED)
        }
        val user = store.getUserById(claims.subject) ?: return@Filter Response(Status.UNAUTHORIZED)
        val aclVer = claims["acl_ver"] as? Int ?: return@Filter Response(Status.UNAUTHORIZED)
        if (aclVer != user.aclVer) {
            return@Filter Response(Status.UNAUTHORIZED)
        }
        val tenantId = claims["tenant_id"] as? String
        if (tenantId != null && !store.verifyMembership(user.id, tenantId)) {
            return@Filter Response(Status.FORBIDDEN)
        }
        val authContext = AuthContext(
            sub = claims.subject,
            email = user.email,
            tenantId = tenantId,
            tenantRole = claims["tenant_role"] as? String ?: "tenant_member",
            groups = claimList(claims, "groups"),
            permissions = claimList(claims, "permissions"),
            aclVer = aclVer,
            issuedAt = claims.issuedAt.toInstant(),
            expiresAt = claims.expiration.toInstant(),
        )
        next(request.withAuthContext(authContext))
    }
}

private fun claimList(claims: Claims, field: String): List<String> =
    (claims[field] as? List<*>)?.filterIsInstance<String>() ?: emptyList()
