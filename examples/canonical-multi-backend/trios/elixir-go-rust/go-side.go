// Seam example: Go workers — NATS subscriber (inbound from Elixir) + gRPC caller (outbound to Rust)
// Seam 1: Go ← Elixir (NATS JetStream) — Go subscribes to "work.tasks.dispatch"
// Seam 2: Go → Rust (gRPC) — Go calls KernelService.Transform for each task
// Loop-back: Go → Elixir (NATS JetStream) — Go publishes completion to "work.tasks.completed"
// Not a full application. See context/stacks/trio-elixir-go-rust.md.
//
// The three seam interactions in this file are clearly labeled:
//   (1) NATS durable subscriber on "work.tasks.dispatch" (inbound from Elixir)
//   (2) gRPC client calling Rust KernelService.Transform (outbound to Rust)
//   (3) NATS publisher on "work.tasks.completed" (loop-back to Elixir)

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
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
	pb "github.com/example/elixir-go-rust/gen/kernel/v1"
)

// TaskEvent is the shape published by Elixir to "work.tasks.dispatch"
type TaskEvent struct {
	PayloadVersion int      `json:"payload_version"`
	TaskID         string   `json:"task_id"`
	CorrelationID  string   `json:"correlation_id"`
	PublishedAt    string   `json:"published_at"`
	TaskType       string   `json:"task_type"`
	Data           TaskData `json:"data"`
}

type TaskData struct {
	Values    []float64 `json:"values"`
	Operation string    `json:"operation"`
}

// CompletionEvent is published by Go to "work.tasks.completed" (loop-back to Elixir)
type CompletionEvent struct {
	PayloadVersion int    `json:"payload_version"`
	TaskID         string `json:"task_id"`
	CorrelationID  string `json:"correlation_id"`
	PublishedAt    string `json:"published_at"`
	ResultSummary  string `json:"result_summary"`
	DurationNs     int64  `json:"duration_ns"`
}

var (
	nc           *nats.Conn
	js           nats.JetStreamContext
	kernelConn   *grpc.ClientConn
	kernelClient pb.KernelServiceClient
)

const (
	streamName      = "WORK_TASKS"
	dispatchSubject = "work.tasks.dispatch"
	completedSubject = "work.tasks.completed"
)

func main() {
	natsURL := os.Getenv("NATS_URL")
	if natsURL == "" {
		natsURL = nats.DefaultURL
	}
	rustGRPCAddr := os.Getenv("RUST_GRPC_ADDR")
	if rustGRPCAddr == "" {
		rustGRPCAddr = "localhost:50051"
	}
	httpPort := os.Getenv("HTTP_PORT")
	if httpPort == "" {
		httpPort = "8080"
	}

	// ── Seam 1 setup: connect to NATS JetStream ──
	var err error
	nc, err = nats.Connect(natsURL)
	if err != nil {
		log.Fatalf("NATS connect error: %v", err)
	}
	defer nc.Close()

	js, err = nc.JetStream()
	if err != nil {
		log.Fatalf("JetStream context error: %v", err)
	}

	// Ensure WORK_TASKS stream exists (idempotent; Elixir may also create it on startup)
	if err := ensureStream(); err != nil {
		log.Fatalf("ensure stream: %v", err)
	}

	// ── Seam 2 setup: connect to Rust gRPC kernel ──
	kernelConn, err = grpc.Dial(rustGRPCAddr, grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		log.Fatalf("Rust gRPC dial error: %v", err)
	}
	defer kernelConn.Close()
	kernelClient = pb.NewKernelServiceClient(kernelConn)

	// ── Seam 1: subscribe to "work.tasks.dispatch" as durable consumer ──
	// Durable push subscription: multiple Go workers share the "go-workers" consumer.
	// NATS JetStream distributes messages across active subscribers — natural work queue.
	// Messages published before Go starts are retained by JetStream and delivered on connect.
	sub, err := js.Subscribe(
		dispatchSubject,
		handleTaskDispatch,
		nats.Durable("go-workers"),
		nats.ManualAck(),
		nats.AckWait(30*time.Second),
	)
	if err != nil {
		log.Fatalf("NATS subscribe error: %v", err)
	}
	defer sub.Unsubscribe()
	log.Printf("go-workers: subscribed to %s (durable consumer: go-workers)", dispatchSubject)

	http.HandleFunc("/healthz", handleHealthz)
	log.Printf("go-workers: HTTP listening on :%s", httpPort)
	if err := http.ListenAndServe(":"+httpPort, nil); err != nil {
		log.Fatalf("HTTP server error: %v", err)
	}
}

// handleTaskDispatch processes each task dispatched by Elixir via NATS.
// Three seam interactions happen here in sequence:
//
//	(1) Decode the NATS message — inbound from Elixir
//	(2) Call Rust gRPC KernelService.Transform — outbound to Rust
//	(3) Publish completion event to "work.tasks.completed" — loop-back to Elixir
func handleTaskDispatch(msg *nats.Msg) {
	// ── Seam interaction (1): decode task event from Elixir ──
	var event TaskEvent
	if err := json.Unmarshal(msg.Data, &event); err != nil {
		log.Printf("error decoding task event: %v", err)
		msg.Nak()
		return
	}
	log.Printf("task received from NATS: task_id=%s operation=%s values=%v",
		event.TaskID, event.Data.Operation, event.Data.Values)

	// ── Seam interaction (2): call Rust KernelService.Transform via gRPC ──
	start := time.Now()
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	resp, err := kernelClient.Transform(ctx, &pb.TransformRequest{
		Operation:  event.Data.Operation,
		Values:     event.Data.Values,
		WindowSize: 0,
	})
	if err != nil {
		log.Printf("Rust gRPC error for task_id=%s: %v", event.TaskID, err)
		msg.Nak()
		return
	}
	durationNs := time.Since(start).Nanoseconds()
	log.Printf("Rust result: task_id=%s operation=%s result=%v duration_ns=%d",
		event.TaskID, resp.Method, resp.Result, durationNs)

	// Ack the NATS message after Rust confirms success.
	// Ack signals durable commitment — the message is removed from the work queue.
	msg.Ack()

	// ── Seam interaction (3): publish completion to "work.tasks.completed" → Elixir ──
	resultSummary := fmt.Sprintf("%s %d values", event.Data.Operation, len(resp.Result))
	completion := CompletionEvent{
		PayloadVersion: 1,
		TaskID:         event.TaskID,
		CorrelationID:  event.CorrelationID,
		PublishedAt:    time.Now().UTC().Format(time.RFC3339),
		ResultSummary:  resultSummary,
		DurationNs:     durationNs,
	}
	payload, _ := json.Marshal(completion)
	if _, err := js.Publish(completedSubject, payload); err != nil {
		log.Printf("error publishing completion for task_id=%s: %v", event.TaskID, err)
		return
	}
	log.Printf("completion published: task_id=%s subject=%s result_summary=%q",
		event.TaskID, completedSubject, resultSummary)
}

func ensureStream() error {
	_, err := js.AddStream(&nats.StreamConfig{
		Name:     streamName,
		Subjects: []string{"work.tasks.>"},
		MaxAge:   24 * time.Hour,
	})
	if err != nil && err != nats.ErrStreamNameAlreadyInUse {
		return fmt.Errorf("AddStream: %w", err)
	}
	return nil
}

// GET /healthz: checks NATS connectivity and Rust gRPC reachability
func handleHealthz(w http.ResponseWriter, r *http.Request) {
	natsOK := nc.IsConnected()

	// Check Rust gRPC: attempt a minimal Transform call
	ctx, cancel := context.WithTimeout(r.Context(), 2*time.Second)
	defer cancel()
	_, rustErr := kernelClient.Transform(ctx, &pb.TransformRequest{
		Operation: "mean",
		Values:    []float64{1.0},
	})
	rustOK := rustErr == nil

	w.Header().Set("Content-Type", "application/json")
	if natsOK && rustOK {
		fmt.Fprint(w, `{"status":"ok"}`)
		return
	}
	w.WriteHeader(http.StatusServiceUnavailable)
	fmt.Fprintf(w, `{"status":"degraded","nats_ok":%v,"rust_ok":%v}`, natsOK, rustOK)
}
