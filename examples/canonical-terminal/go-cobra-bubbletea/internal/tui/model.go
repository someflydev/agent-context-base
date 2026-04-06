package tui

import (
	"fmt"

	"github.com/agent-context-base/taskflow-go-bubbletea/internal/core"
	tea "github.com/charmbracelet/bubbletea"
)

type Model struct {
	jobs        []core.Job
	events      []core.Event
	cursor      int
	failedOnly  bool
	interval    int
	statusLabel string
}

func NewModel(jobs []core.Job, events []core.Event, interval int) Model {
	return Model{
		jobs:        core.SortJobs(jobs),
		events:      events,
		interval:    interval,
		statusLabel: "all",
	}
}

func (m Model) Init() tea.Cmd {
	return tea.ClearScrollArea
}

func (m Model) visibleJobs() []core.Job {
	if !m.failedOnly {
		return m.jobs
	}
	return core.FilterJobs(m.jobs, string(core.StatusFailed), "")
}

func (m Model) selectedJob() *core.Job {
	jobs := m.visibleJobs()
	if len(jobs) == 0 {
		return nil
	}
	if m.cursor >= len(jobs) {
		m.cursor = len(jobs) - 1
	}
	job := jobs[m.cursor]
	return &job
}

func (m Model) helpText() string {
	return fmt.Sprintf("TaskFlow Monitor | q quit | r refresh | f failed-only=%v | interval=%ds", m.failedOnly, m.interval)
}
