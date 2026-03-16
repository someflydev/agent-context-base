// Seam example: Go gateway — gRPC caller (Rust) + REST caller (Python)
// This file shows only the seam layer: Rust gRPC client setup, Python REST
// client, the pipeline (Go → Rust → Python), and health endpoints.
// Not a full application. See context/stacks/trio-go-rust-python.md.
//
// Pipeline: POST /process → call Rust Preprocess gRPC → call Python /score → return result.

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

	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
	pb "github.com/example/go-rust-python/gen/processing/v1"
)

var rustConn   *grpc.ClientConn
var rustClient pb.ProcessServiceClient
var pythonURL  string

func main() {
	rustGRPCURL := os.Getenv("RUST_GRPC_URL")
	if rustGRPCURL == "" {
		rustGRPCURL = "localhost:50051"
	}
	pythonURL = os.Getenv("PYTHON_SCORE_URL")
	if pythonURL == "" {
		pythonURL = "http://localhost:8003"
	}

	// Connect to Rust gRPC server
	var err error
	rustConn, err = grpc.Dial(rustGRPCURL, grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		log.Fatalf("failed to connect to Rust gRPC: %v", err)
	}
	defer rustConn.Close()
	rustClient = pb.NewProcessServiceClient(rustConn)

	http.HandleFunc("/process", handleProcess)
	http.HandleFunc("/healthz", handleHealthz)

	log.Println("go-service listening on :8080")
	if err := http.ListenAndServe(":8080", nil); err != nil {
		log.Fatalf("server error: %v", err)
	}
}

// POST /process: {"document": "...", "doc_id": "..."}
// Pipeline: call Rust Preprocess gRPC → call Python /score → return result
func handleProcess(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
		return
	}
	var body struct {
		Document string `json:"document"`
		DocID    string `json:"doc_id"`
	}
	if err := json.NewDecoder(r.Body).Decode(&body); err != nil {
		http.Error(w, "invalid json", http.StatusBadRequest)
		return
	}

	ctx, cancel := context.WithTimeout(r.Context(), 5*time.Second)
	defer cancel()

	// ── Seam A↔B: call Rust gRPC Preprocess ──
	preprocessResp, err := rustClient.Preprocess(ctx, &pb.PreprocessRequest{
		Document: body.Document,
		DocId:    body.DocID,
	})
	if err != nil {
		log.Printf("rust gRPC error for doc_id=%s: %v", body.DocID, err)
		http.Error(w, "preprocessing failed", http.StatusBadGateway)
		return
	}
	log.Printf("rust preprocess doc_id=%s token_count=%d features=%v",
		body.DocID, preprocessResp.TokenCount, preprocessResp.Features)

	// ── Seam B↔C: call Python REST /score with Rust-produced features ──
	scoreResult, err := callPythonScore(ctx, body.DocID, preprocessResp.Features, int(preprocessResp.TokenCount))
	if err != nil {
		log.Printf("python score error for doc_id=%s: %v", body.DocID, err)
		http.Error(w, "scoring failed", http.StatusBadGateway)
		return
	}
	log.Printf("python score doc_id=%s score=%f category=%s",
		body.DocID, scoreResult["score"], scoreResult["category"])

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(scoreResult)
}

type pythonScoreRequest struct {
	DocID      string    `json:"doc_id"`
	Features   []float64 `json:"features"`
	TokenCount int       `json:"token_count"`
}

func callPythonScore(ctx context.Context, docID string, features []float64, tokenCount int) (map[string]interface{}, error) {
	reqBody, _ := json.Marshal(pythonScoreRequest{
		DocID:      docID,
		Features:   features,
		TokenCount: tokenCount,
	})
	req, err := http.NewRequestWithContext(ctx, http.MethodPost, pythonURL+"/score", bytes.NewReader(reqBody))
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
	var result map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("decode python response: %w", err)
	}
	return result, nil
}

// GET /healthz: checks both Rust gRPC and Python REST connectivity
func handleHealthz(w http.ResponseWriter, r *http.Request) {
	ctx, cancel := context.WithTimeout(r.Context(), 2*time.Second)
	defer cancel()

	// Check Rust gRPC: attempt a trivial Preprocess call
	_, rustErr := rustClient.Preprocess(ctx, &pb.PreprocessRequest{Document: "", DocId: "healthz"})
	// A "healthy" Rust service will return a valid (possibly empty) response
	// An unreachable Rust service will return a connection error
	rustOK := rustErr == nil

	// Check Python REST: probe /healthz
	pythonOK := false
	if req, err := http.NewRequestWithContext(ctx, http.MethodGet, pythonURL+"/healthz", nil); err == nil {
		if resp, err := http.DefaultClient.Do(req); err == nil {
			pythonOK = resp.StatusCode == http.StatusOK
			resp.Body.Close()
		}
	}

	w.Header().Set("Content-Type", "application/json")
	if rustOK && pythonOK {
		fmt.Fprint(w, `{"status":"ok"}`)
		return
	}
	w.WriteHeader(http.StatusServiceUnavailable)
	fmt.Fprintf(w, `{"status":"degraded","rust_ok":%v,"python_ok":%v}`, rustOK, pythonOK)
}
