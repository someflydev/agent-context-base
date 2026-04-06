package tests

import (
	"encoding/json"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strings"
	"testing"
)

var binaryPath string

func TestMain(m *testing.M) {
	tmpDir, err := os.MkdirTemp("", "taskflow-go-tview-*")
	if err != nil {
		panic(err)
	}
	defer os.RemoveAll(tmpDir)

	binaryPath = filepath.Join(tmpDir, "taskflow")
	_, currentFile, _, _ := runtime.Caller(0)
	moduleRoot := filepath.Clean(filepath.Join(filepath.Dir(currentFile), ".."))
	build := exec.Command("go", "build", "-o", binaryPath, ".")
	build.Dir = moduleRoot
	build.Env = append(os.Environ(), "GOCACHE=/tmp/go-build-cache", "GOPATH=/tmp/go-path")
	build.Stdout = os.Stdout
	build.Stderr = os.Stderr
	if err := build.Run(); err != nil {
		panic(err)
	}
	os.Exit(m.Run())
}

func fixturesPath(t *testing.T) string {
	t.Helper()
	root, err := filepath.Abs(filepath.Join("..", "..", "fixtures"))
	if err != nil {
		t.Fatal(err)
	}
	return root
}

func runCommand(t *testing.T, args ...string) ([]byte, error) {
	t.Helper()
	command := exec.Command(binaryPath, append([]string{"--fixtures-path", fixturesPath(t)}, args...)...)
	command.Env = append(os.Environ(), "TERM=dumb")
	return command.CombinedOutput()
}

func TestListTable(t *testing.T) {
	output, err := runCommand(t, "list")
	if err != nil {
		t.Fatal(err, string(output))
	}
	if !strings.Contains(string(output), "## BEGIN_JOBS ##") {
		t.Fatalf("missing marker: %s", output)
	}
}

func TestListJSON(t *testing.T) {
	output, err := runCommand(t, "list", "--output", "json")
	if err != nil {
		t.Fatal(err, string(output))
	}
	var payload []map[string]any
	if err := json.Unmarshal(output, &payload); err != nil {
		t.Fatal(err)
	}
	if len(payload) != 20 {
		t.Fatalf("expected 20 jobs, got %d", len(payload))
	}
}

func TestFilterByStatus(t *testing.T) {
	output, err := runCommand(t, "list", "--status", "done", "--output", "json")
	if err != nil {
		t.Fatal(err, string(output))
	}
	var payload []map[string]any
	if err := json.Unmarshal(output, &payload); err != nil {
		t.Fatal(err)
	}
	for _, job := range payload {
		if job["status"] != "done" {
			t.Fatalf("unexpected status payload: %#v", job)
		}
	}
}

func TestInspectJob(t *testing.T) {
	output, err := runCommand(t, "inspect", "job-001", "--output", "json")
	if err != nil {
		t.Fatal(err, string(output))
	}
	var payload map[string]any
	if err := json.Unmarshal(output, &payload); err != nil {
		t.Fatal(err)
	}
	if payload["id"] != "job-001" {
		t.Fatalf("unexpected payload: %#v", payload)
	}
}

func TestStats(t *testing.T) {
	output, err := runCommand(t, "stats", "--output", "json")
	if err != nil {
		t.Fatal(err, string(output))
	}
	var payload map[string]any
	if err := json.Unmarshal(output, &payload); err != nil {
		t.Fatal(err)
	}
	if payload["total"] != float64(20) {
		t.Fatalf("unexpected payload: %#v", payload)
	}
}

func TestWatchNoTUI(t *testing.T) {
	output, err := runCommand(t, "watch", "--no-tui")
	if err != nil {
		t.Fatal(err, string(output))
	}
	if !strings.Contains(string(output), "## BEGIN_JOBS ##") {
		t.Fatalf("missing jobs marker: %s", output)
	}
}

func TestMissingFixtures(t *testing.T) {
	command := exec.Command(binaryPath, "--fixtures-path", filepath.Join(fixturesPath(t), "missing"), "list")
	output, err := command.CombinedOutput()
	if err == nil {
		t.Fatalf("expected failure: %s", output)
	}
	if !strings.Contains(string(output), "## BEGIN_ERROR ##") {
		t.Fatalf("missing error marker: %s", output)
	}
}
