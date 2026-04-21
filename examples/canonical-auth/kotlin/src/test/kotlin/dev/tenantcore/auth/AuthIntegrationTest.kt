package dev.tenantcore.auth

import com.fasterxml.jackson.module.kotlin.jacksonObjectMapper
import dev.tenantcore.auth.auth.TokenService
import dev.tenantcore.auth.domain.InMemoryStore
import io.jsonwebtoken.Jwts
import org.http4k.core.Method.GET
import org.http4k.core.Method.PATCH
import org.http4k.core.Method.POST
import org.http4k.core.Request
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertTrue
import java.nio.file.Path
import java.util.Date

class AuthIntegrationTest {
    private val store = InMemoryStore.loadFromFixtures(Path.of("..", "domain", "fixtures"))
    private val tokenService = TokenService()
    private val handler = app(store, tokenService)
    private val mapper = jacksonObjectMapper()

    @Test
    fun token_issue_success() {
        val response = handler(
            Request(POST, "/auth/token")
                .header("content-type", "application/json")
                .body("""{"email":"admin@acme.example","password":"password"}"""),
        )
        assertEquals(200, response.status.code)
        val payload = mapper.readValue(response.bodyString(), Map::class.java)
        assertTrue(payload.containsKey("access_token"))
    }

    @Test
    fun token_invalid_credentials() {
        val response = handler(
            Request(POST, "/auth/token")
                .header("content-type", "application/json")
                .body("""{"email":"admin@acme.example","password":"wrong"}"""),
        )
        assertEquals(401, response.status.code)
    }

    @Test
    fun token_expired_rejection() {
        val user = checkNotNull(store.getUserByEmail("admin@acme.example"))
        val token = Jwts.builder()
            .subject(user.id)
            .issuer(TokenService.ISSUER)
            .audience().add(TokenService.AUDIENCE).and()
            .claim("tenant_id", user.tenantId)
            .claim("tenant_role", "tenant_admin")
            .claim("groups", listOf("iam-admins"))
            .claim("permissions", store.getEffectivePermissions(user.id))
            .claim("acl_ver", user.aclVer)
            .issuedAt(Date(System.currentTimeMillis() - 2_000))
            .notBefore(Date(System.currentTimeMillis() - 2_000))
            .expiration(Date(System.currentTimeMillis() - 1_000))
            .signWith(TokenService.defaultSigningKey())
            .compact()

        val response = handler(Request(GET, "/me").header("Authorization", "Bearer $token"))
        assertEquals(401, response.status.code)
    }

    @Test
    fun token_stale_acl_ver() {
        val user = checkNotNull(store.getUserByEmail("admin@acme.example"))
        val token = Jwts.builder()
            .subject(user.id)
            .issuer(TokenService.ISSUER)
            .audience().add(TokenService.AUDIENCE).and()
            .claim("tenant_id", user.tenantId)
            .claim("tenant_role", "tenant_admin")
            .claim("groups", listOf("iam-admins"))
            .claim("permissions", store.getEffectivePermissions(user.id))
            .claim("acl_ver", user.aclVer - 1)
            .issuedAt(Date())
            .notBefore(Date())
            .expiration(Date(System.currentTimeMillis() + 10_000))
            .signWith(TokenService.defaultSigningKey())
            .compact()

        val response = handler(Request(GET, "/me").header("Authorization", "Bearer $token"))
        assertEquals(401, response.status.code)
    }

    @Test
    fun get_me_success() {
        val user = checkNotNull(store.getUserByEmail("admin@acme.example"))
        val token = tokenService.issueToken(user, store)
        val response = handler(Request(GET, "/me").header("Authorization", "Bearer $token"))
        assertEquals(200, response.status.code)
    }

    @Test
    fun get_me_unauthorized() {
        val response = handler(Request(GET, "/me"))
        assertEquals(401, response.status.code)
    }

    @Test
    fun rbac_permission_granted() {
        val user = checkNotNull(store.getUserByEmail("admin@acme.example"))
        val token = tokenService.issueToken(user, store)
        val response = handler(Request(GET, "/users").header("Authorization", "Bearer $token"))
        assertEquals(200, response.status.code)
    }

    @Test
    fun rbac_permission_denied() {
        val user = checkNotNull(store.getUserByEmail("bob@acme.example"))
        val token = tokenService.issueToken(user, store)
        val response = handler(
            Request(POST, "/groups")
                .header("Authorization", "Bearer $token")
                .header("content-type", "application/json")
                .body("""{"slug":"extra","name":"Extra"}"""),
        )
        assertEquals(403, response.status.code)
    }

    @Test
    fun cross_tenant_denial() {
        val user = checkNotNull(store.getUserByEmail("admin@acme.example"))
        val target = checkNotNull(store.getUserByEmail("admin@globex.example"))
        val token = tokenService.issueToken(user, store)
        val response = handler(Request(GET, "/users/${target.id}").header("Authorization", "Bearer $token"))
        assertEquals(403, response.status.code)
    }

    @Test
    fun super_admin_access() {
        val user = checkNotNull(store.getUserByEmail("superadmin@tenantcore.dev"))
        val token = tokenService.issueToken(user, store)
        val response = handler(Request(GET, "/admin/tenants").header("Authorization", "Bearer $token"))
        assertEquals(200, response.status.code)
    }

    @Test
    fun super_admin_tenant_scoped_denial() {
        val user = checkNotNull(store.getUserByEmail("superadmin@tenantcore.dev"))
        val token = tokenService.issueToken(user, store)
        val response = handler(Request(GET, "/users").header("Authorization", "Bearer $token"))
        assertEquals(403, response.status.code)
    }

    @Test
    fun me_allowed_routes_match_permissions() {
        val user = checkNotNull(store.getUserByEmail("admin@acme.example"))
        val token = tokenService.issueToken(user, store)
        val response = handler(Request(GET, "/me").header("Authorization", "Bearer $token"))
        val payload = mapper.readValue(response.bodyString(), Map::class.java)
        val allowedRoutes = payload["allowed_routes"] as List<Map<String, Any?>>
        assertTrue(allowedRoutes.any { it["path"] == "/users" })
        assertFalse(allowedRoutes.any { it["path"] == "/admin/tenants" })
    }
}
