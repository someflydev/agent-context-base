package tui

import (
	"fmt"
	"strings"

	"github.com/agent-context-base/taskflow-go-bubbletea/internal/core"
	"github.com/charmbracelet/lipgloss"
)

var (
	headerStyle  = lipgloss.NewStyle().Bold(true).Border(lipgloss.NormalBorder())
	panelStyle   = lipgloss.NewStyle().Border(lipgloss.NormalBorder()).Padding(0, 1)
	doneStyle    = lipgloss.NewStyle().Foreground(lipgloss.Color("2"))
	failStyle    = lipgloss.NewStyle().Foreground(lipgloss.Color("1"))
	runStyle     = lipgloss.NewStyle().Foreground(lipgloss.Color("3"))
	pendingStyle = lipgloss.NewStyle().Foreground(lipgloss.Color("8"))
)

func statusStyle(status core.JobStatus) lipgloss.Style {
	switch status {
	case core.StatusDone:
		return doneStyle
	case core.StatusFailed:
		return failStyle
	case core.StatusRunning:
		return runStyle
	default:
		return pendingStyle
	}
}

func (m Model) View() string {
	jobs := m.visibleJobs()
	left := []string{"ID       NAME                     STATUS   DURATION"}
	for index, job := range jobs {
		cursor := " "
		if index == m.cursor {
			cursor = ">"
		}
		duration := "-"
		if job.DurationS != nil {
			duration = fmt.Sprintf("%.1fs", *job.DurationS)
		}
		line := fmt.Sprintf("%s %-8s %-24s %-8s %-8s", cursor, job.ID, job.Name, job.Status, duration)
		left = append(left, statusStyle(job.Status).Render(line))
	}

	detail := []string{"No jobs available"}
	if job := m.selectedJob(); job != nil {
		detail = []string{
			fmt.Sprintf("ID: %s", job.ID),
			fmt.Sprintf("Name: %s", job.Name),
			fmt.Sprintf("Status: %s", job.Status),
			fmt.Sprintf("Started: %s", valueOr(job.StartedAt, "-")),
			fmt.Sprintf("Duration (s): %s", durationOr(job.DurationS)),
			fmt.Sprintf("Tags: %s", strings.Join(job.Tags, ", ")),
			fmt.Sprintf("Events loaded: %d", len(m.events)),
			"",
			"Output:",
		}
		for _, line := range job.OutputLines {
			detail = append(detail, "  - "+line)
		}
	}

	leftPanel := panelStyle.Width(64).Render(strings.Join(left, "\n"))
	rightPanel := panelStyle.Width(48).Render(strings.Join(detail, "\n"))
	return strings.Join([]string{
		headerStyle.Width(115).Render(m.helpText()),
		lipgloss.JoinHorizontal(lipgloss.Top, leftPanel, rightPanel),
	}, "\n")
}

func valueOr(value *string, fallback string) string {
	if value == nil {
		return fallback
	}
	return *value
}

func durationOr(value *float64) string {
	if value == nil {
		return "-"
	}
	return fmt.Sprintf("%.1f", *value)
}
