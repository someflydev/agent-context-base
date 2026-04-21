package dev.tenantcore.auth.auth;

import dev.tenantcore.auth.domain.Group;
import dev.tenantcore.auth.domain.InMemoryStore;
import dev.tenantcore.auth.domain.InMemoryStore.Membership;
import dev.tenantcore.auth.domain.User;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.JwtException;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.MalformedJwtException;
import org.springframework.stereotype.Service;

import javax.crypto.SecretKey;
import java.util.Date;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
public class JwtService {

    private static final String ISSUER = "tenantcore-auth";
    private static final String AUDIENCE = "tenantcore-api";
    private static final long EXPIRY_MILLIS = 900_000L;

    private final SecretKey signingKey;

    public JwtService(SecretKey jwtSigningKey) {
        this.signingKey = jwtSigningKey;
    }

    public String issueToken(User user, InMemoryStore store) {
        Membership membership = store.getActiveMembership(user.id())
            .orElseThrow(() -> new IllegalStateException("No active membership for " + user.id()));
        String tenantRole = membership.tenantRole();
        String tenantId = membership.tenantId();

        List<String> groups = tenantId == null
            ? List.of()
            : store.getGroupsForUser(user.id(), tenantId).stream()
            .map(Group::slug)
            .collect(Collectors.toList());
        List<String> permissions = store.getEffectivePermissions(user.id());
        if ("super_admin".equals(tenantRole)) {
            permissions = store.getAdminPermissions();
        }

        Date now = new Date();
        Date expiration = new Date(now.getTime() + EXPIRY_MILLIS);

        return Jwts.builder()
            .subject(user.id())
            .issuer(ISSUER)
            .audience().add(AUDIENCE).and()
            .claim("tenant_id", tenantId)
            .claim("tenant_role", tenantRole)
            .claim("groups", groups)
            .claim("permissions", permissions)
            .claim("acl_ver", user.aclVer())
            .claim("jti", UUID.randomUUID().toString())
            .issuedAt(now)
            .notBefore(now)
            .expiration(expiration)
            .signWith(signingKey)
            .compact();
    }

    public Claims parseToken(String token) throws JwtException {
        Claims claims = Jwts.parser()
            .verifyWith(signingKey)
            .build()
            .parseSignedClaims(token)
            .getPayload();
        if (!ISSUER.equals(claims.getIssuer())) {
            throw new MalformedJwtException("Unexpected issuer");
        }
        if (claims.getAudience() == null || !claims.getAudience().contains(AUDIENCE)) {
            throw new MalformedJwtException("Unexpected audience");
        }
        return claims;
    }
}
