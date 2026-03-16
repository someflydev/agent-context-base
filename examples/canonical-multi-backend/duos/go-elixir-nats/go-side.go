// This is a seam-focused example.
// For a full application scaffold, see context/archetypes/multi-backend-service.md.
//
// go-side.go — Go service: connects to NATS, ensures stream exists,
// publishes a typed domain event, and exposes /healthz.
//
// Dependencies (go.mod):
//   github.com/nats-io/nats.go v1.37.0

package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/nats-io/nats.go"
)

// UserCreatedEvent is the typed event published to NATS JetStream.
// All fields are required; consumers reject unknown payload_version values.
type UserCreatedEvent struct {
	PayloadVersion int    `json:"payload_version"`
	CorrelationID  string `json:"correlation_id"`
	PublishedAt    string `json:"published_at"`
	TenantID       string `json:"tenant_id"`
	EventType      string `json:"event_type"`
	UserID         string `json:"user_id"`
}

const streamName = "DOMAIN_EVENTS"
const streamSubject = "events.>"

var nc *nats.Conn

func main() {
	natsURL := os.Getenv("NATS_URL")
	if natsURL == "" {
		natsURL = nats.DefaultURL
	}

	var err error
	nc, err = nats.Connect(natsURL,
		nats.RetryOnFailedConnect(true),
		nats.MaxReconnects(10),
		nats.ReconnectWait(2*time.Second),
	)
	if err != nil {
		log.Fatalf("NATS connect failed: %v", err)
	}
	defer nc.Drain()
	log.Printf("connected to NATS at %s", natsURL)

	if err := ensureStream(nc); err != nil {
		log.Fatalf("stream setup failed: %v", err)
	}

	if err := publishSampleEvent(nc); err != nil {
		log.Printf("publish error: %v", err)
	}

	http.HandleFunc("/healthz", healthzHandler)
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}
	log.Printf("HTTP listening on :%s", port)
	log.Fatal(http.ListenAndServe(":"+port, nil))
}

// ensureStream creates the DOMAIN_EVENTS stream if it does not exist.
// Safe to call on every boot — AddStream is idempotent when config matches.
func ensureStream(nc *nats.Conn) error {
	js, err := nc.JetStream()
	if err != nil {
		return fmt.Errorf("jetstream context: %w", err)
	}
	_, err = js.AddStream(&nats.StreamConfig{
		Name:     streamName,
		Subjects: []string{streamSubject},
		MaxAge:   24 * time.Hour,
	})
	if err != nil {
		// ErrStreamNameAlreadyInUse means it already exists — not an error.
		if err == nats.ErrStreamNameAlreadyInUse {
			return nil
		}
		return fmt.Errorf("add stream: %w", err)
	}
	log.Printf("stream %q ensured", streamName)
	return nil
}

// publishSampleEvent publishes one UserCreatedEvent to demonstrate the seam.
func publishSampleEvent(nc *nats.Conn) error {
	js, err := nc.JetStream()
	if err != nil {
		return fmt.Errorf("jetstream context: %w", err)
	}

	event := UserCreatedEvent{
		PayloadVersion: 1,
		CorrelationID:  "req-demo-001",
		PublishedAt:    time.Now().UTC().Format(time.RFC3339),
		TenantID:       "demo",
		EventType:      "user.created",
		UserID:         "u123",
	}
	payload, err := json.Marshal(event)
	if err != nil {
		return fmt.Errorf("marshal event: %w", err)
	}

	subject := "events.user." + event.TenantID
	ack, err := js.Publish(subject, payload)
	if err != nil {
		return fmt.Errorf("publish to %q: %w", subject, err)
	}
	log.Printf("published %s to %q (seq=%d)", event.EventType, subject, ack.Sequence)
	return nil
}

// healthzHandler returns 200 if NATS is connected, 503 otherwise.
func healthzHandler(w http.ResponseWriter, r *http.Request) {
	if nc == nil || !nc.IsConnected() {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusServiceUnavailable)
		fmt.Fprintln(w, `{"status":"degraded","reason":"nats disconnected"}`)
		return
	}
	w.Header().Set("Content-Type", "application/json")
	fmt.Fprintln(w, `{"status":"ok"}`)
}
