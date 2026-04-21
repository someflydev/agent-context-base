package dev.tenantcore.auth.auth

import dev.tenantcore.auth.domain.InMemoryStore
import dev.tenantcore.auth.domain.User
import io.jsonwebtoken.Claims
import io.jsonwebtoken.JwtException
import io.jsonwebtoken.Jwts
import io.jsonwebtoken.MalformedJwtException
import java.util.Date
import java.util.UUID
import javax.crypto.SecretKey
import javax.crypto.spec.SecretKeySpec

class TokenService(
    private val signingKey: SecretKey = defaultSigningKey(),
) {
    fun issueToken(user: User, store: InMemoryStore): String {
        val membership = store.getActiveMembership(user.id)
            ?: error("No active membership for ${user.id}")
        val tenantId = membership.tenantId
        val tenantRole = membership.tenantRole
        val permissions = when (tenantRole) {
            "super_admin" -> store.getAdminPermissions()
            else -> store.getEffectivePermissions(user.id)
        }
        val groups = if (tenantId == null) {
            emptyList()
        } else {
            store.getGroupsForUser(user.id, tenantId).map { it.slug }
        }
        val now = Date()
        val expiration = Date(now.time + EXPIRY_MILLIS)

        return Jwts.builder()
            .subject(user.id)
            .issuer(ISSUER)
            .audience().add(AUDIENCE).and()
            .claim("tenant_id", tenantId)
            .claim("tenant_role", tenantRole)
            .claim("groups", groups)
            .claim("permissions", permissions)
            .claim("acl_ver", user.aclVer)
            .claim("jti", UUID.randomUUID().toString())
            .issuedAt(now)
            .notBefore(now)
            .expiration(expiration)
            .signWith(signingKey)
            .compact()
    }

    fun parseToken(token: String): Claims {
        val claims = Jwts.parser()
            .verifyWith(signingKey)
            .build()
            .parseSignedClaims(token)
            .payload
        if (claims.issuer != ISSUER) {
            throw MalformedJwtException("Unexpected issuer")
        }
        if (!claims.audience.contains(AUDIENCE)) {
            throw MalformedJwtException("Unexpected audience")
        }
        return claims
    }

    companion object {
        const val ISSUER = "tenantcore-auth"
        const val AUDIENCE = "tenantcore-api"
        const val EXPIRY_MILLIS = 900_000L

        fun defaultSigningKey(): SecretKey =
            SecretKeySpec(
                "this-is-a-fallback-secret-key-for-testing-only-12345678901234567890"
                    .toByteArray(Charsets.UTF_8),
                "HmacSHA256",
            )
    }
}
