package tui

import tea "github.com/charmbracelet/bubbletea"

func (m Model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.KeyMsg:
		switch msg.String() {
		case "q", "ctrl+c":
			return m, tea.Quit
		case "down":
			if m.cursor < len(m.visibleJobs())-1 {
				m.cursor++
			}
		case "up":
			if m.cursor > 0 {
				m.cursor--
			}
		case "f":
			m.failedOnly = !m.failedOnly
			m.cursor = 0
		case "r":
			return m, func() tea.Msg { return refreshMsg{} }
		}
	case refreshMsg:
		return m, nil
	}
	return m, nil
}
