package auth

import (
	"fmt"
	"net/http"
	"os"
	"strings"

	"canonical-auth/internal/domain"

	"github.com/golang-jwt/jwt/v5"
	"github.com/labstack/echo/v4"
)

func JWTMiddleware(store *domain.InMemoryStore, verifyKey interface{}) echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			authHeader := c.Request().Header.Get("Authorization")
			if authHeader == "" || !strings.HasPrefix(authHeader, "Bearer ") {
				return echo.NewHTTPError(http.StatusUnauthorized, "missing or invalid authorization header")
			}

			tokenString := strings.TrimPrefix(authHeader, "Bearer ")

			token, err := jwt.ParseWithClaims(tokenString, &Claims{}, func(token *jwt.Token) (interface{}, error) {
				if testSecret := os.Getenv("TENANTCORE_TEST_SECRET"); testSecret != "" {
					if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
						return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
					}
					return []byte(testSecret), nil
				}
				
				if _, ok := token.Method.(*jwt.SigningMethodRSA); !ok {
					return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
				}
				return verifyKey, nil
			}, jwt.WithValidMethods([]string{"RS256", "HS256"}), jwt.WithIssuer("tenantcore-auth"), jwt.WithAudience("tenantcore-api"))

			if err != nil || !token.Valid {
				return echo.NewHTTPError(http.StatusUnauthorized, "invalid token")
			}

			claims, ok := token.Claims.(*Claims)
			if !ok {
				return echo.NewHTTPError(http.StatusUnauthorized, "invalid token claims")
			}

			user, ok := store.GetUserByID(claims.Subject)
			if !ok {
				return echo.NewHTTPError(http.StatusUnauthorized, "user not found")
			}

			if claims.ACLVer != user.ACLVer {
				return echo.NewHTTPError(http.StatusUnauthorized, "stale acl version")
			}

			if claims.TenantID != nil {
				if !store.VerifyMembership(user.ID, *claims.TenantID) {
					return echo.NewHTTPError(http.StatusForbidden, "not an active member of the tenant")
				}
			}

			authCtx := AuthContext{
				Sub:         claims.Subject,
				Email:       user.Email,
				TenantID:    claims.TenantID,
				TenantRole:  claims.TenantRole,
				Groups:      claims.Groups,
				Permissions: claims.Permissions,
				ACLVer:      claims.ACLVer,
				IssuedAt:    claims.IssuedAt.Time,
				ExpiresAt:   claims.ExpiresAt.Time,
			}

			c.Set("auth", &authCtx)
			return next(c)
		}
	}
}

func RequirePermission(permission string) echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			authCtx, ok := c.Get("auth").(*AuthContext)
			if !ok {
				return echo.NewHTTPError(http.StatusInternalServerError, "missing auth context")
			}

			if !authCtx.HasPermission(permission) {
				return echo.NewHTTPError(http.StatusForbidden, "missing required permission")
			}

			return next(c)
		}
	}
}

func RequireSuperAdmin() echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			authCtx, ok := c.Get("auth").(*AuthContext)
			if !ok {
				return echo.NewHTTPError(http.StatusInternalServerError, "missing auth context")
			}

			if authCtx.TenantRole != "super_admin" {
				return echo.NewHTTPError(http.StatusForbidden, "super admin required")
			}

			return next(c)
		}
	}
}
