package analytics

import (
	"sort"

	"analytics-workbench-go/internal/data"
	"analytics-workbench-go/internal/filters"
)

type EventCountSeries struct {
	Dates         []string
	Counts        []int
	ByEnvironment map[string][]int
}

func AggregateEvents(events []data.Event, f filters.FilterState) EventCountSeries {
	if len(events) == 0 {
		return EventCountSeries{ByEnvironment: make(map[string][]int)}
	}

	dateSet := make(map[string]bool)
	envSet := make(map[string]bool)
	countsByDateEnv := make(map[string]map[string]int) // date -> env -> count
	totalByDate := make(map[string]int)

	for _, e := range events {
		if !f.ContainsEnvironment(e.Environment) {
			continue
		}
		
		t := parseDate(e.Timestamp)
		if !f.InDateRange(t) {
			continue
		}
		if !f.ContainsService(e.Service) {
			continue
		}

		dateStr := e.Timestamp[:10]
		dateSet[dateStr] = true
		envSet[e.Environment] = true

		if countsByDateEnv[dateStr] == nil {
			countsByDateEnv[dateStr] = make(map[string]int)
		}
		countsByDateEnv[dateStr][e.Environment] += e.Count
		totalByDate[dateStr] += e.Count
	}

	if len(dateSet) == 0 {
		return EventCountSeries{ByEnvironment: make(map[string][]int)}
	}

	var dates []string
	for d := range dateSet {
		dates = append(dates, d)
	}
	sort.Strings(dates)

	counts := make([]int, len(dates))
	byEnv := make(map[string][]int)
	for env := range envSet {
		byEnv[env] = make([]int, len(dates))
	}

	for i, d := range dates {
		counts[i] = totalByDate[d]
		for env := range envSet {
			byEnv[env][i] = countsByDateEnv[d][env]
		}
	}

	return EventCountSeries{
		Dates:         dates,
		Counts:        counts,
		ByEnvironment: byEnv,
	}
}
