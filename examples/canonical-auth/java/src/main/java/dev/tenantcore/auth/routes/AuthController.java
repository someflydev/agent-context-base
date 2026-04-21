package dev.tenantcore.auth.routes;

import dev.tenantcore.auth.auth.JwtService;
import dev.tenantcore.auth.domain.InMemoryStore;
import dev.tenantcore.auth.domain.User;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

@RestController
public class AuthController {

    private final JwtService jwtService;
    private final InMemoryStore store;

    public AuthController(JwtService jwtService, InMemoryStore store) {
        this.jwtService = jwtService;
        this.store = store;
    }

    public record TokenRequest(String email, String password) {}

    @PostMapping("/auth/token")
    public ResponseEntity<?> token(@RequestBody TokenRequest req) {
        User user = store.getUserByEmail(req.email());
        if (user == null || !"password".equals(req.password())) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        }

        String token = jwtService.issueToken(user, store);
        return ResponseEntity.ok(Map.of(
            "access_token", token,
            "token_type", "Bearer",
            "expires_in", 900
        ));
    }
}
