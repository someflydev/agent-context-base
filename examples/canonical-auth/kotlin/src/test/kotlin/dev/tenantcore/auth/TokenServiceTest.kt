package dev.tenantcore.auth

import dev.tenantcore.auth.auth.TokenService
import dev.tenantcore.auth.domain.InMemoryStore
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertNotNull
import kotlin.test.assertTrue
import java.nio.file.Path

class TokenServiceTest {
    private val store = InMemoryStore.loadFromFixtures(Path.of("..", "domain", "fixtures"))
    private val tokenService = TokenService()

    @Test
    fun testIssueToken_AllClaimsPresent() {
        val user = store.getUserByEmail("admin@acme.example")
        assertNotNull(user)

        val claims = tokenService.parseToken(tokenService.issueToken(user, store))
        assertEquals(user.id, claims.subject)
        assertEquals("tenantcore-auth", claims.issuer)
        assertTrue(claims.audience.contains("tenantcore-api"))
        assertEquals(user.tenantId, claims["tenant_id"])
        assertEquals("tenant_admin", claims["tenant_role"])
        assertTrue((claims["groups"] as List<*>).isNotEmpty() || claims.containsKey("groups"))
        assertTrue((claims["permissions"] as List<*>).isNotEmpty())
        assertEquals(user.aclVer, claims["acl_ver"])
        assertNotNull(claims.id)
    }

    @Test
    fun testIssueToken_ExpiryIs15Minutes() {
        val user = checkNotNull(store.getUserByEmail("admin@acme.example"))
        val claims = tokenService.parseToken(tokenService.issueToken(user, store))
        assertEquals(TokenService.EXPIRY_MILLIS, claims.expiration.time - claims.issuedAt.time)
    }

    @Test
    fun testIssueToken_PermissionsMatchStore() {
        val user = checkNotNull(store.getUserByEmail("admin@acme.example"))
        val claims = tokenService.parseToken(tokenService.issueToken(user, store))
        val tokenPermissions = (claims["permissions"] as List<*>).filterIsInstance<String>()
        val storePermissions = store.getEffectivePermissions(user.id)
        assertEquals(storePermissions.size, tokenPermissions.size)
        assertTrue(tokenPermissions.containsAll(storePermissions))
    }
}
