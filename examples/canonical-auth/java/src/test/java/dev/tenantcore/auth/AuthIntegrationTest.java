package dev.tenantcore.auth;

import io.jsonwebtoken.Jwts;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import dev.tenantcore.auth.auth.JwtService;
import dev.tenantcore.auth.domain.InMemoryStore;
import dev.tenantcore.auth.domain.User;

import javax.crypto.SecretKey;
import java.util.Date;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
public class AuthIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private JwtService jwtService;

    @Autowired
    private InMemoryStore store;

    @Autowired
    private SecretKey jwtSigningKey;

    @Test
    public void token_issue_success() throws Exception {
        mockMvc.perform(post("/auth/token")
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"email\":\"admin@acme.example\", \"password\":\"password\"}"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.access_token").exists())
            .andExpect(jsonPath("$.token_type").value("Bearer"));
    }

    @Test
    public void token_invalid_credentials() throws Exception {
        mockMvc.perform(post("/auth/token")
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"email\":\"admin@acme.example\", \"password\":\"wrong\"}"))
            .andExpect(status().isUnauthorized());
    }

    @Test
    public void token_expired_rejection() throws Exception {
        User user = store.getUserByEmail("admin@acme.example");
        Date past = new Date(System.currentTimeMillis() - 100000);
        String token = Jwts.builder()
            .subject(user.id())
            .issuer("tenantcore-auth")
            .claim("tenant_id", user.tenantId())
            .claim("acl_ver", user.aclVer())
            .expiration(past)
            .signWith(jwtSigningKey)
            .compact();

        mockMvc.perform(get("/me").header("Authorization", "Bearer " + token))
            .andExpect(status().isUnauthorized());
    }

    @Test
    public void token_stale_acl_ver() throws Exception {
        User user = store.getUserByEmail("admin@acme.example");
        String token = Jwts.builder()
            .subject(user.id())
            .issuer("tenantcore-auth")
            .claim("tenant_id", user.tenantId())
            .claim("acl_ver", user.aclVer() - 1) // stale
            .expiration(new Date(System.currentTimeMillis() + 100000))
            .signWith(jwtSigningKey)
            .compact();

        mockMvc.perform(get("/me").header("Authorization", "Bearer " + token))
            .andExpect(status().isUnauthorized());
    }

    @Test
    public void get_me_success() throws Exception {
        User user = store.getUserByEmail("admin@acme.example");
        String token = jwtService.issueToken(user, store);

        mockMvc.perform(get("/me").header("Authorization", "Bearer " + token))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.sub").value(user.id()));
    }

    @Test
    public void get_me_unauthorized() throws Exception {
        mockMvc.perform(get("/me"))
            .andExpect(status().isUnauthorized());
    }

    @Test
    public void rbac_permission_granted() throws Exception {
        User user = store.getUserByEmail("admin@acme.example");
        String token = jwtService.issueToken(user, store);

        mockMvc.perform(get("/users").header("Authorization", "Bearer " + token))
            .andExpect(status().isOk());
    }

    @Test
    public void rbac_permission_denied() throws Exception {
        User user = store.getUserByEmail("bob@acme.example");
        String token = jwtService.issueToken(user, store);

        mockMvc.perform(post("/groups")
                .header("Authorization", "Bearer " + token)
                .contentType(MediaType.APPLICATION_JSON)
                .content("{}"))
            .andExpect(status().isForbidden());
    }

    @Test
    public void cross_tenant_denial() throws Exception {
        User user = store.getUserByEmail("admin@acme.example");
        String token = jwtService.issueToken(user, store);
        
        // Target a user in a different tenant (Globex)
        User target = store.getUserByEmail("admin@globex.example");

        mockMvc.perform(get("/users/" + target.id())
                .header("Authorization", "Bearer " + token))
            .andExpect(status().isForbidden());
    }

    @Test
    public void super_admin_access() throws Exception {
        User user = store.getUserByEmail("superadmin@tenantcore.dev");
        String token = jwtService.issueToken(user, store);

        mockMvc.perform(get("/admin/tenants")
                .header("Authorization", "Bearer " + token))
            .andExpect(status().isOk());
    }

    @Test
    public void super_admin_tenant_scoped_denial() throws Exception {
        User user = store.getUserByEmail("superadmin@tenantcore.dev");
        String token = jwtService.issueToken(user, store);

        mockMvc.perform(get("/users").header("Authorization", "Bearer " + token))
            .andExpect(status().isForbidden());
    }

    @Test
    public void me_allowed_routes_match_permissions() throws Exception {
        User user = store.getUserByEmail("admin@acme.example");
        String token = jwtService.issueToken(user, store);

        mockMvc.perform(get("/me").header("Authorization", "Bearer " + token))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.allowed_routes[?(@.path == '/users')]").exists());
            
        // Test that a route not allowed is omitted
        mockMvc.perform(get("/me").header("Authorization", "Bearer " + token))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.allowed_routes[?(@.path == '/admin/tenants')]").doesNotExist());
    }
}
