package dev.tenantcore.auth;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;

import dev.tenantcore.auth.auth.JwtService;
import dev.tenantcore.auth.domain.InMemoryStore;
import dev.tenantcore.auth.domain.User;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;
import static org.hamcrest.Matchers.*;

@SpringBootTest
@AutoConfigureMockMvc
public class MeControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private JwtService jwtService;

    @Autowired
    private InMemoryStore store;

    @Test
    public void testMeResponse_ContainsRequiredFields() throws Exception {
        User user = store.getUserByEmail("admin@acme.example");
        String token = jwtService.issueToken(user, store);

        mockMvc.perform(get("/me").header("Authorization", "Bearer " + token))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.sub").value(user.id()))
            .andExpect(jsonPath("$.email").value(user.email()))
            .andExpect(jsonPath("$.tenant_id").value(user.tenantId()))
            .andExpect(jsonPath("$.tenant_role").value("tenant_admin"))
            .andExpect(jsonPath("$.permissions").isArray())
            .andExpect(jsonPath("$.groups").isArray())
            .andExpect(jsonPath("$.allowed_routes").isArray())
            .andExpect(jsonPath("$.issued_at").exists())
            .andExpect(jsonPath("$.expires_at").exists());
    }

    @Test
    public void testMeResponse_AllowedRoutesFiltered() throws Exception {
        User user = store.getUserByEmail("alice@acme.example");
        String token = jwtService.issueToken(user, store);

        mockMvc.perform(get("/me").header("Authorization", "Bearer " + token))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.allowed_routes[?(@.path == '/users' && @.method == 'GET')]").exists())
            // Should not have admin route
            .andExpect(jsonPath("$.allowed_routes[?(@.path == '/admin/tenants')]").doesNotExist());
    }

    @Test
    public void testMeResponse_SuperAdminShape() throws Exception {
        User user = store.getUserByEmail("superadmin@tenantcore.dev");
        String token = jwtService.issueToken(user, store);

        mockMvc.perform(get("/me").header("Authorization", "Bearer " + token))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.tenant_id").value(nullValue()))
            .andExpect(jsonPath("$.tenant_role").value("super_admin"))
            .andExpect(jsonPath("$.groups").isEmpty())
            .andExpect(jsonPath("$.allowed_routes[?(@.path == '/admin/tenants')]").exists())
            .andExpect(jsonPath("$.allowed_routes[?(@.path == '/users')]").doesNotExist());
    }
}
