package dev.tenantcore.auth.auth;

import dev.tenantcore.auth.domain.InMemoryStore;
import dev.tenantcore.auth.domain.User;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.JwtException;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.List;
import java.util.stream.Collectors;

@Component
public class JwtFilter extends OncePerRequestFilter {

    private final JwtService jwtService;
    private final InMemoryStore store;

    public JwtFilter(JwtService jwtService, InMemoryStore store) {
        this.jwtService = jwtService;
        this.store = store;
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {

        String authHeader = request.getHeader("Authorization");
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            filterChain.doFilter(request, response);
            return;
        }

        String token = authHeader.substring(7).trim();
        Claims claims;
        try {
            claims = jwtService.parseToken(token);
        } catch (JwtException e) {
            response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
            return;
        }

        User user = store.getUserById(claims.getSubject());
        if (user == null) {
            response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
            return;
        }

        Integer aclVer = claims.get("acl_ver", Integer.class);
        if (aclVer == null || aclVer != user.aclVer()) {
            response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
            return;
        }

        String tenantId = claims.get("tenant_id", String.class);
        if (tenantId != null && !store.verifyMembership(user.id(), tenantId)) {
            response.setStatus(HttpServletResponse.SC_FORBIDDEN);
            return;
        }

        List<String> groups = getClaimList(claims, "groups");
        List<String> permissions = getClaimList(claims, "permissions");

        AuthContext authContext = new AuthContext(
            claims.getSubject(),
            user.email(),
            tenantId,
            claims.get("tenant_role", String.class),
            groups != null ? groups : List.of(),
            permissions != null ? permissions : List.of(),
            aclVer,
            claims.getIssuedAt().toInstant(),
            claims.getExpiration().toInstant()
        );

        List<SimpleGrantedAuthority> authorities = authContext.permissions().stream()
            .map(SimpleGrantedAuthority::new)
            .collect(Collectors.toList());

        UsernamePasswordAuthenticationToken auth = new UsernamePasswordAuthenticationToken(
            authContext, null, authorities);
        SecurityContextHolder.getContext().setAuthentication(auth);

        filterChain.doFilter(request, response);
    }

    private List<String> getClaimList(Claims claims, String claimName) {
        Object claim = claims.get(claimName);
        if (!(claim instanceof List<?> rawValues)) {
            return List.of();
        }
        return rawValues.stream()
            .filter(String.class::isInstance)
            .map(String.class::cast)
            .toList();
    }
}
