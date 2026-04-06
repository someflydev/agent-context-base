package tui

import (
	"fmt"
	"strings"

	"github.com/agent-context-base/taskflow-go-tview/internal/core"
	"github.com/gdamore/tcell/v2"
	"github.com/rivo/tview"
)

func Run(jobs []core.Job, events []core.Event, interval int) error {
	app := tview.NewApplication()
	table := tview.NewTable().SetBorders(false).SetSelectable(true, false)
	detail := tview.NewTextView().SetDynamicColors(true).SetWrap(true)
	header := tview.NewTextView().
		SetText(fmt.Sprintf("TaskFlow Monitor | q quit | r refresh | f widget filter | interval=%ds", interval))

	sorted := core.SortJobs(jobs)
	failedOnly := false

	render := func() {
		table.Clear()
		table.SetCell(0, 0, tview.NewTableCell("ID").SetSelectable(false).SetAttributes(tcell.AttrBold))
		table.SetCell(0, 1, tview.NewTableCell("NAME").SetSelectable(false).SetAttributes(tcell.AttrBold))
		table.SetCell(0, 2, tview.NewTableCell("STATUS").SetSelectable(false).SetAttributes(tcell.AttrBold))
		table.SetCell(0, 3, tview.NewTableCell("DURATION").SetSelectable(false).SetAttributes(tcell.AttrBold))

		visible := sorted
		if failedOnly {
			visible = core.FilterJobs(sorted, string(core.StatusFailed), "")
		}
		for index, job := range visible {
			row := index + 1
			table.SetCell(row, 0, tview.NewTableCell(job.ID))
			table.SetCell(row, 1, tview.NewTableCell(job.Name))
			table.SetCell(row, 2, tview.NewTableCell(string(job.Status)).SetTextColor(statusColor(job.Status)))
			table.SetCell(row, 3, tview.NewTableCell(duration(job.DurationS)))
		}
		if len(visible) > 0 {
			updateDetail(detail, visible[0], len(events))
		} else {
			detail.SetText("No jobs available")
		}
	}

	table.SetSelectionChangedFunc(func(row int, _ int) {
		visible := sorted
		if failedOnly {
			visible = core.FilterJobs(sorted, string(core.StatusFailed), "")
		}
		if row <= 0 || row > len(visible) {
			return
		}
		updateDetail(detail, visible[row-1], len(events))
	})
	table.SetInputCapture(func(event *tcell.EventKey) *tcell.EventKey {
		switch event.Rune() {
		case 'q':
			app.Stop()
			return nil
		case 'f':
			failedOnly = !failedOnly
			render()
			return nil
		case 'r':
			render()
			return nil
		}
		return event
	})

	render()
	layout := tview.NewFlex().
		SetDirection(tview.FlexRow).
		AddItem(header, 1, 0, false).
		AddItem(tview.NewFlex().
			AddItem(table, 0, 3, true).
			AddItem(detail, 0, 2, false), 0, 1, true)

	return app.SetRoot(layout, true).Run()
}

func updateDetail(view *tview.TextView, job core.Job, eventCount int) {
	lines := []string{
		fmt.Sprintf("ID: %s", job.ID),
		fmt.Sprintf("Name: %s", job.Name),
		fmt.Sprintf("Status: %s", job.Status),
		fmt.Sprintf("Started: %s", valueOr(job.StartedAt, "-")),
		fmt.Sprintf("Duration (s): %s", duration(job.DurationS)),
		fmt.Sprintf("Tags: %s", strings.Join(job.Tags, ", ")),
		fmt.Sprintf("Events loaded: %d", eventCount),
		"",
		"Output:",
	}
	for _, line := range job.OutputLines {
		lines = append(lines, "  - "+line)
	}
	view.SetText(strings.Join(lines, "\n"))
}

func statusColor(status core.JobStatus) tcell.Color {
	switch status {
	case core.StatusDone:
		return tcell.ColorGreen
	case core.StatusFailed:
		return tcell.ColorRed
	case core.StatusRunning:
		return tcell.ColorYellow
	default:
		return tcell.ColorGray
	}
}

func valueOr(value *string, fallback string) string {
	if value == nil {
		return fallback
	}
	return *value
}

func duration(value *float64) string {
	if value == nil {
		return "-"
	}
	return fmt.Sprintf("%.1f", *value)
}
