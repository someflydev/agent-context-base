package dev.tenantcore.auth;

import dev.tenantcore.auth.auth.JwtService;
import dev.tenantcore.auth.domain.InMemoryStore;
import dev.tenantcore.auth.domain.User;
import io.jsonwebtoken.Claims;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import javax.crypto.SecretKey;
import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

public class JwtServiceTest {

    private InMemoryStore store;
    private JwtService jwtService;

    @BeforeEach
    public void setup() throws Exception {
        store = InMemoryStore.loadFromFixtures(Path.of("../domain/fixtures"));
        SecretKey key = new SecretKeySpec("this-is-a-fallback-secret-key-for-testing-only-12345678901234567890".getBytes(StandardCharsets.UTF_8), "HmacSHA256");
        jwtService = new JwtService(key);
    }

    @Test
    public void testIssueToken_AllClaimsPresent() {
        User user = store.getUserByEmail("admin@acme.example");
        assertNotNull(user);

        String token = jwtService.issueToken(user, store);
        Claims claims = jwtService.parseToken(token);

        assertEquals(user.id(), claims.getSubject());
        assertEquals("tenantcore-auth", claims.getIssuer());
        assertEquals("tenantcore-api", claims.getAudience().iterator().next());
        assertEquals(user.tenantId(), claims.get("tenant_id"));
        assertEquals("tenant_admin", claims.get("tenant_role"));
        assertTrue(claims.containsKey("groups"));
        assertTrue(claims.containsKey("permissions"));
        assertEquals(user.aclVer(), claims.get("acl_ver", Integer.class));
        assertNotNull(claims.getId()); // jti
    }

    @Test
    public void testIssueToken_ExpiryIs15Minutes() {
        User user = store.getUserByEmail("admin@acme.example");
        String token = jwtService.issueToken(user, store);
        Claims claims = jwtService.parseToken(token);

        long diff = claims.getExpiration().getTime() - claims.getIssuedAt().getTime();
        assertEquals(900_000L, diff, 1000); // 15 mins exact
    }

    @Test
    public void testIssueToken_PermissionsMatchStore() {
        User user = store.getUserByEmail("admin@acme.example");
        String token = jwtService.issueToken(user, store);
        Claims claims = jwtService.parseToken(token);

        List<String> tokenPerms = claims.get("permissions", List.class);
        List<String> storePerms = store.getEffectivePermissions(user.id());

        assertEquals(storePerms.size(), tokenPerms.size());
        assertTrue(tokenPerms.containsAll(storePerms));
    }
}
