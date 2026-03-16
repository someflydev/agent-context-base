// This is a seam-focused example.
// For a full application scaffold, see context/archetypes/multi-backend-service.md.
//
// go-side.go — Go gateway: calls the Python scoring service at /score,
// exposes /run-inference to trigger a round-trip, and exposes /healthz
// with a downstream health probe that degrades if Python is unreachable.
//
// Dependencies: stdlib only (net/http, encoding/json, os, log, fmt)

package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"
)

// ScoreRequest matches the Python Pydantic model for POST /score.
type ScoreRequest struct {
	Features []float64 `json:"features"`
	Model    string    `json:"model"`
}

// ScoreResponse matches the Python Pydantic model returned from POST /score.
type ScoreResponse struct {
	Score     float64 `json:"score"`
	Label     string  `json:"label"`
	LatencyMs float64 `json:"latency_ms"`
}

var pythonScoreURL string

func main() {
	pythonScoreURL = os.Getenv("PYTHON_SCORE_URL")
	if pythonScoreURL == "" {
		pythonScoreURL = "http://python-service:8001"
	}

	mux := http.NewServeMux()
	mux.HandleFunc("/run-inference", runInferenceHandler)
	mux.HandleFunc("/healthz", healthzHandler)

	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}
	log.Printf("Go gateway listening on :%s  python_score_url=%s", port, pythonScoreURL)
	log.Fatal(http.ListenAndServe(":"+port, mux))
}

// runInferenceHandler calls the Python scoring service with sample features
// and returns the result to the HTTP caller.
func runInferenceHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet && r.Method != http.MethodPost {
		http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
		return
	}

	req := ScoreRequest{
		Features: []float64{3.1, 7.2, 5.5, 2.9},
		Model:    "fraud-v3",
	}

	result, err := callScore(req)
	if err != nil {
		log.Printf("score call failed: %v", err)
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusServiceUnavailable)
		fmt.Fprintf(w, `{"detail":"scoring service unavailable"}`)
		return
	}

	log.Printf("inference result: score=%.3f label=%s latency_ms=%.2f",
		result.Score, result.Label, result.LatencyMs)

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(result)
}

// callScore makes a POST /score request to the Python service.
// Returns a structured error if Python is unreachable or returns a non-200 status.
func callScore(req ScoreRequest) (*ScoreResponse, error) {
	body, err := json.Marshal(req)
	if err != nil {
		return nil, fmt.Errorf("marshal request: %w", err)
	}

	client := &http.Client{Timeout: 5 * time.Second}
	resp, err := client.Post(
		pythonScoreURL+"/score",
		"application/json",
		bytes.NewReader(body),
	)
	if err != nil {
		return nil, fmt.Errorf("python scoring unreachable: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("python scoring returned %d", resp.StatusCode)
	}

	var result ScoreResponse
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("decode response: %w", err)
	}
	return &result, nil
}

// healthzHandler returns 200 if both the Go service is up and Python /healthz is reachable.
// Returns 503 with a degraded status if the downstream Python service is unreachable.
// This downstream health probe pattern is important: a caller's health check must reflect
// the health of its dependencies, not just its own process.
func healthzHandler(w http.ResponseWriter, r *http.Request) {
	client := &http.Client{Timeout: 2 * time.Second}
	resp, err := client.Get(pythonScoreURL + "/healthz")

	w.Header().Set("Content-Type", "application/json")

	if err != nil || resp.StatusCode != http.StatusOK {
		w.WriteHeader(http.StatusServiceUnavailable)
		fmt.Fprintln(w, `{"status":"degraded","reason":"python scoring unreachable"}`)
		return
	}
	defer resp.Body.Close()
	fmt.Fprintln(w, `{"status":"ok"}`)
}
