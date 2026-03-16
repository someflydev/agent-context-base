// Seam example: Go domain service — REST server (inbound from Node) + REST caller (outbound to Python)
// Seam 1: Go ← Node (REST) — receives GET /users/:id/recommendations from the GraphQL BFF
// Seam 2: Go → Python (REST) — calls POST /recommend on the Python ML service
// Not a full application. See context/stacks/trio-node-go-python.md.
//
// Go acts as the internal orchestrator: it creates stub user data, calls Python ML
// for recommendation scores, and returns a combined result to Node.
// Node makes one call to Go; Go handles the downstream Python call transparently.

package main

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/labstack/echo/v4"
)

var pythonMLURL string

func main() {
	pythonMLURL = os.Getenv("PYTHON_ML_URL")
	if pythonMLURL == "" {
		pythonMLURL = "http://localhost:8002"
	}
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	e := echo.New()
	e.HideBanner = true

	// ── Seam 1: GET /users/:id/recommendations — inbound from Node GraphQL BFF ──
	e.GET("/users/:id/recommendations", handleGetUserRecommendations)
	// ── Health endpoint: probes Python ML service downstream ──
	e.GET("/healthz", handleHealthz)

	log.Printf("go-service: Echo listening on :%s", port)
	e.Logger.Fatal(e.Start(":" + port))
}

// handleGetUserRecommendations is the seam handler for Node → Go:
//  1. Creates stub user data for the given userId
//  2. Calls Python POST /recommend with user features (seam 2: Go → Python)
//  3. Returns the combined {user, recommendations} response to Node
func handleGetUserRecommendations(c echo.Context) error {
	userID := c.Param("id")
	log.Printf("GET /users/%s/recommendations — received from Node BFF", userID)

	// Stub user data — in production this would be a database lookup
	user := map[string]string{
		"id":    userID,
		"name":  "User " + userID,
		"email": userID + "@example.com",
	}

	// Derive stub ML features from userID length (deterministic for the seam example)
	features := deriveFeatures(userID)

	// ── Seam 2: call Python POST /recommend — outbound to Python ML service ──
	ctx, cancel := context.WithTimeout(c.Request().Context(), 5*time.Second)
	defer cancel()

	recommendations, err := callPythonRecommend(ctx, userID, features)
	if err != nil {
		log.Printf("Python ML error for userId=%s: %v", userID, err)
		return c.JSON(http.StatusBadGateway, map[string]string{
			"error": "ml service unavailable",
		})
	}
	log.Printf("Python ML result: userId=%s recommendations=%d", userID, len(recommendations))

	return c.JSON(http.StatusOK, map[string]interface{}{
		"user":            user,
		"recommendations": recommendations,
	})
}

// deriveFeatures produces a deterministic float slice from a userId string.
// In production, these would come from a feature store or user profile database.
func deriveFeatures(userID string) []float64 {
	features := make([]float64, len(userID))
	for i, ch := range userID {
		features[i] = float64(int(ch)%10) / 10.0
	}
	if len(features) == 0 {
		return []float64{0.5}
	}
	return features
}

// pythonRecommendRequest is the body sent to Python POST /recommend
type pythonRecommendRequest struct {
	UserID   string    `json:"user_id"`
	Features []float64 `json:"features"`
}

// pythonRecommendation is one item from Python's response list
type pythonRecommendation struct {
	Score    float64 `json:"score"`
	Category string  `json:"category"`
	Reason   string  `json:"reason"`
}

func callPythonRecommend(ctx context.Context, userID string, features []float64) ([]pythonRecommendation, error) {
	reqBody, err := json.Marshal(pythonRecommendRequest{
		UserID:   userID,
		Features: features,
	})
	if err != nil {
		return nil, fmt.Errorf("marshal request: %w", err)
	}

	req, err := http.NewRequestWithContext(
		ctx, http.MethodPost, pythonMLURL+"/recommend", bytes.NewReader(reqBody),
	)
	if err != nil {
		return nil, fmt.Errorf("build request: %w", err)
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("python unreachable: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("python returned %d", resp.StatusCode)
	}

	var result []pythonRecommendation
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("decode python response: %w", err)
	}
	return result, nil
}

// GET /healthz: probes Python ML service; returns degraded if Python is unreachable.
// Downstream health probe pattern: Go is not healthy if its downstream dependency is down.
func handleHealthz(c echo.Context) error {
	ctx, cancel := context.WithTimeout(c.Request().Context(), 2*time.Second)
	defer cancel()

	pythonOK := false
	if req, err := http.NewRequestWithContext(ctx, http.MethodGet, pythonMLURL+"/healthz", nil); err == nil {
		if resp, err := http.DefaultClient.Do(req); err == nil {
			pythonOK = resp.StatusCode == http.StatusOK
			resp.Body.Close()
		}
	}

	if pythonOK {
		return c.JSON(http.StatusOK, map[string]string{
			"status":    "ok",
			"python_ml": "ok",
		})
	}
	return c.JSON(http.StatusServiceUnavailable, map[string]string{
		"status":    "degraded",
		"python_ml": "unavailable",
	})
}
