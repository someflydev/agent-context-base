package validate

import (
	"encoding/json"
	"os"
	"path/filepath"
	"testing"

	"workspace-sync-validator-ozzo/models"
)

func loadWebhookFixture(t *testing.T, name string) models.WebhookPayload {
	t.Helper()
	path := filepath.Join("..", "..", "..", "domain", "fixtures", name)
	data, err := os.ReadFile(path)
	if err != nil {
		t.Fatalf("read fixture: %v", err)
	}
	var payload models.WebhookPayload
	if err := json.Unmarshal(data, &payload); err != nil {
		t.Fatalf("unmarshal fixture: %v", err)
	}
	return payload
}

func TestValidateWebhookPayloadAcceptsValidFixture(t *testing.T) {
	payload := loadWebhookFixture(t, "valid/webhook_payload_sync_completed.json")
	if err := ValidateWebhookPayload(&payload); err != nil {
		t.Fatalf("expected valid payload, got error: %v", err)
	}
}

func TestValidateWebhookPayloadRejectsInvalidNestedData(t *testing.T) {
	payload := loadWebhookFixture(t, "valid/webhook_payload_sync_completed.json")

	var data map[string]interface{}
	if err := json.Unmarshal(payload.Data, &data); err != nil {
		t.Fatalf("decode nested payload: %v", err)
	}
	delete(data, "run_id")
	rewritten, err := json.Marshal(data)
	if err != nil {
		t.Fatalf("re-encode nested payload: %v", err)
	}
	payload.Data = rewritten

	if err := ValidateWebhookPayload(&payload); err == nil {
		t.Fatal("expected invalid nested payload to fail validation")
	}
}
