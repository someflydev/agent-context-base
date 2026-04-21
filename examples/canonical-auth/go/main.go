package main

import (
	"crypto/rand"
	"crypto/rsa"
	"log"
	"net/http"

	"canonical-auth/internal/auth"
	"canonical-auth/internal/domain"
	"canonical-auth/internal/routes"

	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
)

func main() {
	store, err := domain.LoadFromFixtures("")
	if err != nil {
		log.Fatalf("Failed to load fixtures: %v", err)
	}

	privateKey, err := rsa.GenerateKey(rand.Reader, 2048)
	if err != nil {
		log.Fatalf("Failed to generate RSA key: %v", err)
	}
	publicKey := &privateKey.PublicKey

	e := echo.New()
	e.Use(middleware.Logger())
	e.Use(middleware.Recover())

	authRoutes := &routes.AuthRoutes{
		Store:      store,
		SigningKey: privateKey,
	}
	healthRoutes := &routes.HealthRoutes{}
	meRoutes := &routes.MeRoutes{Store: store}
	usersRoutes := &routes.UsersRoutes{Store: store}
	groupsRoutes := &routes.GroupsRoutes{Store: store}
	adminRoutes := &routes.AdminRoutes{Store: store}

	e.POST("/auth/token", authRoutes.Token)
	e.GET("/health", healthRoutes.Health)

	protected := e.Group("", auth.JWTMiddleware(store, publicKey))
	protected.GET("/me", meRoutes.Me)

	protected.GET("/users", usersRoutes.List, auth.RequirePermission("iam:user:read"))
	protected.POST("/users", usersRoutes.Invite, auth.RequirePermission("iam:user:invite"))
	protected.GET("/users/:id", usersRoutes.Get, auth.RequirePermission("iam:user:read"))
	protected.PATCH("/users/:id", usersRoutes.Update, auth.RequirePermission("iam:user:update"))

	protected.GET("/groups", groupsRoutes.List, auth.RequirePermission("iam:group:read"))
	protected.POST("/groups", groupsRoutes.Create, auth.RequirePermission("iam:group:create"))
	protected.POST("/groups/:id/permissions", groupsRoutes.AssignPermission, auth.RequirePermission("iam:group:assign_permission"))
	protected.POST("/groups/:id/users", groupsRoutes.AssignUser, auth.RequirePermission("iam:group:assign_user"))

	protected.GET("/permissions", func(c echo.Context) error {
		return c.JSON(http.StatusOK, store.Permissions)
	}, auth.RequirePermission("iam:permission:read"))

	protected.GET("/admin/tenants", adminRoutes.ListTenants, auth.RequireSuperAdmin())
	protected.POST("/admin/tenants", adminRoutes.CreateTenant, auth.RequireSuperAdmin())

	e.Logger.Fatal(e.Start(":8080"))
}
