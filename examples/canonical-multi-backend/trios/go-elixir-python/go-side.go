// Seam example: Go gateway — NATS JetStream publisher
// This file shows only the seam layer: NATS connection setup, stream
// creation, job publishing, and health endpoint. Not a full application.
// See context/stacks/trio-go-elixir-python.md for architecture context.

package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/nats-io/nats.go"
)

type JobSubmittedEvent struct {
	PayloadVersion int       `json:"payload_version"`
	CorrelationID  string    `json:"correlation_id"`
	PublishedAt    string    `json:"published_at"`
	JobID          string    `json:"job_id"`
	Features       []float64 `json:"features"`
}

var nc *nats.Conn
var js nats.JetStreamContext

func main() {
	natsURL := os.Getenv("NATS_URL")
	if natsURL == "" {
		natsURL = nats.DefaultURL
	}

	var err error
	nc, err = nats.Connect(natsURL)
	if err != nil {
		log.Fatalf("failed to connect to NATS: %v", err)
	}
	defer nc.Close()

	js, err = nc.JetStream()
	if err != nil {
		log.Fatalf("failed to get JetStream context: %v", err)
	}

	// Ensure the JOBS stream exists (idempotent — safe to call on every boot)
	if err := ensureStream(js); err != nil {
		log.Fatalf("failed to ensure stream: %v", err)
	}

	// Publish one demo job on startup to demonstrate the seam
	if err := publishDemoJob(js); err != nil {
		log.Printf("warning: failed to publish demo job: %v", err)
	}

	// HTTP handler: POST /submit-job accepts {"job_id": str, "features": [...]}
	http.HandleFunc("/submit-job", handleSubmitJob)
	http.HandleFunc("/healthz", handleHealthz)

	log.Println("go-service listening on :8080")
	if err := http.ListenAndServe(":8080", nil); err != nil {
		log.Fatalf("server error: %v", err)
	}
}

func ensureStream(js nats.JetStreamContext) error {
	_, err := js.AddStream(&nats.StreamConfig{
		Name:     "JOBS",
		Subjects: []string{"jobs.>"},
		MaxAge:   24 * time.Hour,
	})
	if err != nil && err != nats.ErrStreamNameAlreadyInUse {
		return fmt.Errorf("AddStream: %w", err)
	}
	return nil
}

func publishDemoJob(js nats.JetStreamContext) error {
	event := JobSubmittedEvent{
		PayloadVersion: 1,
		CorrelationID:  "req-demo-001",
		PublishedAt:    time.Now().UTC().Format(time.RFC3339),
		JobID:          "job-demo-001",
		Features:       []float64{1.2, 3.4, 5.6, 7.8},
	}
	payload, err := json.Marshal(event)
	if err != nil {
		return err
	}
	ack, err := js.Publish("jobs.submitted", payload)
	if err != nil {
		return fmt.Errorf("publish: %w", err)
	}
	log.Printf("published job_id=%s to jobs.submitted (seq=%d)", event.JobID, ack.Sequence)
	return nil
}

// POST /submit-job: {"job_id": "...", "features": [...]}
func handleSubmitJob(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
		return
	}
	var body struct {
		JobID    string    `json:"job_id"`
		Features []float64 `json:"features"`
	}
	if err := json.NewDecoder(r.Body).Decode(&body); err != nil {
		http.Error(w, "invalid json", http.StatusBadRequest)
		return
	}
	event := JobSubmittedEvent{
		PayloadVersion: 1,
		CorrelationID:  r.Header.Get("X-Correlation-ID"),
		PublishedAt:    time.Now().UTC().Format(time.RFC3339),
		JobID:          body.JobID,
		Features:       body.Features,
	}
	payload, _ := json.Marshal(event)
	ack, err := js.Publish("jobs.submitted", payload)
	if err != nil {
		log.Printf("error publishing job_id=%s: %v", body.JobID, err)
		http.Error(w, "failed to publish job", http.StatusInternalServerError)
		return
	}
	log.Printf("published job_id=%s to jobs.submitted (seq=%d)", body.JobID, ack.Sequence)
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusAccepted)
	fmt.Fprintf(w, `{"status":"accepted","job_id":%q,"seq":%d}`, body.JobID, ack.Sequence)
}

// GET /healthz: checks NATS connectivity
func handleHealthz(w http.ResponseWriter, r *http.Request) {
	ctx, cancel := context.WithTimeout(r.Context(), 2*time.Second)
	defer cancel()
	_ = ctx

	if !nc.IsConnected() {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusServiceUnavailable)
		fmt.Fprint(w, `{"status":"degraded","reason":"nats disconnected"}`)
		return
	}
	w.Header().Set("Content-Type", "application/json")
	fmt.Fprint(w, `{"status":"ok"}`)
}
