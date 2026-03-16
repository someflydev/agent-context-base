// This is a seam-focused example.
// For a full application scaffold, see context/archetypes/multi-backend-service.md.
//
// go-side.go — Go domain service exposing user data via REST (Echo router).
// Serves as the downstream API that the Node/GraphQL BFF calls.
// Uses stub data — no database dependency — to keep the example self-contained.
//
// Routes:
//   GET  /users       — returns a list of stub users
//   GET  /users/:id   — returns a single user by ID (404 if not found)
//   GET  /healthz     — returns {"status":"ok"}
//
// Environment:
//   PORT  — listen port (default: 8080)
//
// go.mod: module seam-example; require github.com/labstack/echo/v4 v4.12.0

package main

import (
	"net/http"
	"os"

	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
)

type User struct {
	ID        string `json:"id"`
	Name      string `json:"name"`
	Email     string `json:"email"`
	CreatedAt string `json:"created_at"`
}

// Deterministic stub data — ID maps to a fixed user record.
var usersByID = map[string]User{
	"1": {ID: "1", Name: "Alice Chen", Email: "alice@example.com", CreatedAt: "2026-01-01T00:00:00Z"},
	"2": {ID: "2", Name: "Bob Nakamura", Email: "bob@example.com", CreatedAt: "2026-01-15T00:00:00Z"},
	"3": {ID: "3", Name: "Carol Torres", Email: "carol@example.com", CreatedAt: "2026-02-01T00:00:00Z"},
}

var userList = []User{usersByID["1"], usersByID["2"], usersByID["3"]}

func main() {
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	e := echo.New()
	e.HideBanner = true

	// Request logging: method, path, status, latency.
	e.Use(middleware.Logger())

	e.GET("/users", getUsers)
	e.GET("/users/:id", getUserByID)
	e.GET("/healthz", healthz)

	e.Logger.Fatal(e.Start(":" + port))
}

func getUsers(c echo.Context) error {
	return c.JSON(http.StatusOK, userList)
}

func getUserByID(c echo.Context) error {
	id := c.Param("id")
	user, ok := usersByID[id]
	if !ok {
		return c.JSON(http.StatusNotFound, map[string]string{
			"error": "user not found",
			"id":    id,
		})
	}
	return c.JSON(http.StatusOK, user)
}

func healthz(c echo.Context) error {
	return c.JSON(http.StatusOK, map[string]string{"status": "ok"})
}
