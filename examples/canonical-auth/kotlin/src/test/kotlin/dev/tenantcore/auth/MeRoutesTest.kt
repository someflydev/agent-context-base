package dev.tenantcore.auth

import com.fasterxml.jackson.module.kotlin.jacksonObjectMapper
import dev.tenantcore.auth.auth.TokenService
import dev.tenantcore.auth.domain.InMemoryStore
import org.http4k.core.Method.GET
import org.http4k.core.Request
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertNull
import kotlin.test.assertTrue
import java.nio.file.Path

class MeRoutesTest {
    private val store = InMemoryStore.loadFromFixtures(Path.of("..", "domain", "fixtures"))
    private val tokenService = TokenService()
    private val handler = app(store, tokenService)
    private val mapper = jacksonObjectMapper()

    @Test
    fun testMeResponse_ContainsRequiredFields() {
        val user = checkNotNull(store.getUserByEmail("admin@acme.example"))
        val token = tokenService.issueToken(user, store)
        val response = handler(Request(GET, "/me").header("Authorization", "Bearer $token"))

        assertEquals(200, response.status.code)
        val payload = mapper.readValue(response.bodyString(), Map::class.java)
        assertEquals(user.id, payload["sub"])
        assertEquals(user.email, payload["email"])
        assertEquals(user.tenantId, payload["tenant_id"])
        assertEquals("tenant_admin", payload["tenant_role"])
        assertTrue((payload["permissions"] as List<*>).isNotEmpty())
        assertTrue(payload["groups"] is List<*>)
    }

    @Test
    fun testMeResponse_AllowedRoutesFiltered() {
        val user = checkNotNull(store.getUserByEmail("alice@acme.example"))
        val token = tokenService.issueToken(user, store)
        val response = handler(Request(GET, "/me").header("Authorization", "Bearer $token"))
        val payload = mapper.readValue(response.bodyString(), Map::class.java)
        val allowedRoutes = payload["allowed_routes"] as List<Map<String, Any?>>
        assertTrue(allowedRoutes.any { it["path"] == "/users" && it["method"] == "GET" })
        assertFalse(allowedRoutes.any { it["path"] == "/admin/tenants" })
    }

    @Test
    fun testMeResponse_SuperAdminShape() {
        val user = checkNotNull(store.getUserByEmail("superadmin@tenantcore.dev"))
        val token = tokenService.issueToken(user, store)
        val response = handler(Request(GET, "/me").header("Authorization", "Bearer $token"))
        val payload = mapper.readValue(response.bodyString(), Map::class.java)
        val allowedRoutes = payload["allowed_routes"] as List<Map<String, Any?>>
        assertNull(payload["tenant_id"])
        assertEquals("super_admin", payload["tenant_role"])
        assertTrue((payload["groups"] as List<*>).isEmpty())
        assertTrue(allowedRoutes.any { it["path"] == "/admin/tenants" })
        assertFalse(allowedRoutes.any { it["path"] == "/users" })
    }
}
