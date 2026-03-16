// This is a seam-focused example.
// For a full application scaffold, see context/archetypes/multi-backend-service.md.
//
// go-side.go — Go Kafka consumer seam example.
// Subscribes to "domain.orders.enriched" as consumer group "go-risk-workers".
// Processes each message: logs event_type, entity_id, risk_score, correlation_id.
// Commits offsets manually after processing. Exposes GET /healthz.
//
// Dependencies (go.mod):
//   github.com/twmb/franz-go v1.x

package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"strings"
	"time"

	"github.com/twmb/franz-go/pkg/kgo"
)

// OrderEvent is the typed event consumed from the Kafka topic.
// Unknown payload_version values are logged and skipped — treated as DLQ candidates.
type OrderEvent struct {
	PayloadVersion int       `json:"payload_version"`
	CorrelationID  string    `json:"correlation_id"`
	PublishedAt    string    `json:"published_at"`
	TenantID       string    `json:"tenant_id"`
	EventType      string    `json:"event_type"`
	EntityID       string    `json:"entity_id"`
	Data           OrderData `json:"data"`
}

type OrderData struct {
	RiskScore float64 `json:"risk_score"`
	RiskTier  string  `json:"risk_tier"`
}

var kafkaClient *kgo.Client

func main() {
	brokersEnv := os.Getenv("KAFKA_BOOTSTRAP_SERVERS")
	if brokersEnv == "" {
		brokersEnv = "kafka:9092"
	}
	brokers := strings.Split(brokersEnv, ",")

	groupID := os.Getenv("GROUP_ID")
	if groupID == "" {
		groupID = "go-risk-workers"
	}

	topic := "domain.orders.enriched"

	var err error
	kafkaClient, err = kgo.NewClient(
		kgo.SeedBrokers(brokers...),
		kgo.ConsumerGroup(groupID),
		kgo.ConsumeTopics(topic),
		kgo.DisableAutoCommit(),
	)
	if err != nil {
		log.Fatalf("kafka client init failed: %v", err)
	}
	defer kafkaClient.Close()

	log.Printf("subscribed to %q as consumer group %q", topic, groupID)

	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}
	http.HandleFunc("/healthz", healthzHandler)
	go func() {
		log.Printf("HTTP listening on :%s", port)
		log.Fatal(http.ListenAndServe(":"+port, nil))
	}()

	consumeLoop(context.Background())
}

// consumeLoop polls Kafka, processes each record, and commits offsets manually.
func consumeLoop(ctx context.Context) {
	for {
		fetches := kafkaClient.PollFetches(ctx)
		if err := fetches.Err(); err != nil {
			log.Printf("fetch error: %v", err)
			time.Sleep(time.Second)
			continue
		}

		var toCommit []*kgo.Record
		fetches.EachRecord(func(r *kgo.Record) {
			if err := processRecord(r); err != nil {
				// DLQ path: log the failure. In production, produce to
				// "domain.orders.enriched.dlq" with original message + error context.
				log.Printf("DLQ: failed to process topic=%s offset=%d err=%v",
					r.Topic, r.Offset, err)
			}
			// Always commit — even failed records advance the offset so the
			// partition does not stall. DLQ'd records are committed here too.
			toCommit = append(toCommit, r)
		})

		if len(toCommit) > 0 {
			if err := kafkaClient.CommitRecords(ctx, toCommit...); err != nil {
				log.Printf("commit failed: %v", err)
			}
		}
	}
}

// processRecord decodes one Kafka record and logs the seam-relevant fields.
func processRecord(r *kgo.Record) error {
	var event OrderEvent
	if err := json.Unmarshal(r.Value, &event); err != nil {
		return fmt.Errorf("parse error: %w", err)
	}
	if event.PayloadVersion != 1 {
		return fmt.Errorf("unknown payload_version %d", event.PayloadVersion)
	}
	log.Printf("received event_type=%s entity_id=%s risk_score=%.2f risk_tier=%s correlation_id=%s",
		event.EventType, event.EntityID, event.Data.RiskScore, event.Data.RiskTier, event.CorrelationID)
	return nil
}

// healthzHandler returns 200 if the Kafka client is initialised, 503 otherwise.
func healthzHandler(w http.ResponseWriter, r *http.Request) {
	if kafkaClient == nil {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusServiceUnavailable)
		fmt.Fprintln(w, `{"status":"degraded","reason":"kafka client not initialised"}`)
		return
	}
	w.Header().Set("Content-Type", "application/json")
	fmt.Fprintln(w, `{"status":"ok"}`)
}
