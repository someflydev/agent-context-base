package routes

import (
	"net/http"

	"canonical-auth/internal/auth"
	"canonical-auth/internal/domain"

	"github.com/labstack/echo/v4"
)

type AuthRoutes struct {
	Store      *domain.InMemoryStore
	SigningKey interface{}
}

type TokenRequest struct {
	Email    string `json:"email"`
	Password string `json:"password"`
}

func (r *AuthRoutes) Token(c echo.Context) error {
	var req TokenRequest
	if err := c.Bind(&req); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, "invalid request body")
	}

	user, ok := r.Store.GetUserByEmail(req.Email)
	// Hardcoded password check for the canonical example
	if !ok || req.Password != "password123" {
		return echo.NewHTTPError(http.StatusUnauthorized, "invalid credentials")
	}

	token, err := auth.IssueToken(user, r.Store, r.SigningKey)
	if err != nil {
		return echo.NewHTTPError(http.StatusInternalServerError, "failed to issue token")
	}

	return c.JSON(http.StatusOK, map[string]string{
		"access_token": token,
		"token_type":   "Bearer",
	})
}
