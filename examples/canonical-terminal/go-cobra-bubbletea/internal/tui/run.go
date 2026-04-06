package tui

import (
	"github.com/agent-context-base/taskflow-go-bubbletea/internal/core"
	tea "github.com/charmbracelet/bubbletea"
)

func Run(jobs []core.Job, events []core.Event, interval int) error {
	model := NewModel(jobs, events, interval)
	_, err := tea.NewProgram(model, tea.WithAltScreen()).Run()
	return err
}
