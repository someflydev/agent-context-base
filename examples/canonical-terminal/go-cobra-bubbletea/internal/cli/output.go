package cli

import (
	"encoding/json"
	"fmt"
	"strings"

	"github.com/agent-context-base/taskflow-go-bubbletea/internal/core"
)

func PrintMarkerBlock(begin string, content string, end string) {
	fmt.Println(begin)
	if content != "" {
		fmt.Println(content)
	}
	fmt.Println(end)
}

func PrintJSON(value any) error {
	payload, err := json.MarshalIndent(value, "", "  ")
	if err != nil {
		return err
	}
	fmt.Println(string(payload))
	return nil
}

func PrintError(err error) error {
	PrintMarkerBlock("## BEGIN_ERROR ##", err.Error(), "## END_ERROR ##")
	return err
}

func JobsTable(jobs []core.Job) string {
	lines := []string{fmt.Sprintf("%-8s %-24s %-8s %-12s %s", "ID", "NAME", "STATUS", "DURATION", "TAGS")}
	for _, job := range jobs {
		duration := "-"
		if job.DurationS != nil {
			duration = fmt.Sprintf("%.1fs", *job.DurationS)
		}
		lines = append(lines, fmt.Sprintf(
			"%-8s %-24s %-8s %-12s %s",
			job.ID, job.Name, job.Status, duration, strings.Join(job.Tags, ","),
		))
	}
	return strings.Join(lines, "\n")
}

func JobPlain(job core.Job) string {
	lines := []string{
		fmt.Sprintf("ID: %s", job.ID),
		fmt.Sprintf("Name: %s", job.Name),
		fmt.Sprintf("Status: %s", job.Status),
		fmt.Sprintf("Started: %s", deref(job.StartedAt, "-")),
		fmt.Sprintf("Duration (s): %s", durationValue(job.DurationS)),
		fmt.Sprintf("Tags: %s", strings.Join(job.Tags, ", ")),
		"Output:",
	}
	for _, line := range job.OutputLines {
		lines = append(lines, "  - "+line)
	}
	return strings.Join(lines, "\n")
}

func StatsPlain(stats core.Stats) string {
	return strings.Join([]string{
		fmt.Sprintf("Total jobs: %d", stats.Total),
		fmt.Sprintf("Done: %d", stats.ByStatus[string(core.StatusDone)]),
		fmt.Sprintf("Failed: %d", stats.ByStatus[string(core.StatusFailed)]),
		fmt.Sprintf("Running: %d", stats.ByStatus[string(core.StatusRunning)]),
		fmt.Sprintf("Pending: %d", stats.ByStatus[string(core.StatusPending)]),
		fmt.Sprintf("Average duration (s): %.2f", stats.AvgDurationS),
		fmt.Sprintf("Failure rate: %.2f", stats.FailureRate),
	}, "\n")
}

func durationValue(value *float64) string {
	if value == nil {
		return "-"
	}
	return fmt.Sprintf("%.1f", *value)
}

func deref(value *string, fallback string) string {
	if value == nil {
		return fallback
	}
	return *value
}
