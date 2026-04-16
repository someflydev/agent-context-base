package analytics

import (
	"time"

	"analytics-workbench-go/internal/data"
	"analytics-workbench-go/internal/filters"
)

type EventHeatmap struct {
	Hours  []int
	Days   []string
	Counts [][]int // Counts[dayIdx][hour]
}

func AggregateHeatmap(events []data.Event, f filters.FilterState) EventHeatmap {
	daysOrder := []string{"Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"}
	hours := make([]int, 24)
	for i := 0; i < 24; i++ {
		hours[i] = i
	}

	var filtered []data.Event
	for _, e := range events {
		if !f.ContainsEnvironment(e.Environment) {
			continue
		}
		if !f.ContainsService(e.Service) {
			continue
		}
		
		t := parseDate(e.Timestamp)
		if !f.InDateRange(t) {
			continue
		}
		filtered = append(filtered, e)
	}

	counts := make([][]int, 7)
	for i := 0; i < 7; i++ {
		counts[i] = make([]int, 24)
	}

	if len(filtered) == 0 {
		return EventHeatmap{
			Hours:  hours,
			Days:   daysOrder,
			Counts: counts,
		}
	}

	for _, e := range filtered {
		t, err := time.Parse("2006-01-02T15:04:05", e.Timestamp)
		if err != nil {
			t = parseDate(e.Timestamp) // fallback
		}
		hour := t.Hour()
		
		// time.Weekday() 0 = Sunday, 1 = Monday. We want 0 = Mon.
		dayIdx := int(t.Weekday()) - 1
		if dayIdx < 0 {
			dayIdx = 6
		}
		counts[dayIdx][hour] += e.Count
	}

	return EventHeatmap{
		Hours:  hours,
		Days:   daysOrder,
		Counts: counts,
	}
}
