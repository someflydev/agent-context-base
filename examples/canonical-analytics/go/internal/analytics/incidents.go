package analytics

import (
	"analytics-workbench-go/internal/data"
	"analytics-workbench-go/internal/filters"
)

type IncidentSeverity struct {
	Severities     []string
	Counts         []int
	MTTRBySeverity map[string]float64
}

func AggregateIncidents(incidents []data.Incident, services []data.Service, f filters.FilterState) IncidentSeverity {
	validServices := make(map[string]bool)
	if len(services) > 0 {
		for _, s := range services {
			validServices[s.Name] = true
		}
	} else {
		for _, i := range incidents {
			validServices[i.Service] = true
		}
	}

	var filtered []data.Incident
	for _, i := range incidents {
		if !validServices[i.Service] {
			continue
		}
		if !f.ContainsService(i.Service) {
			continue
		}
		if !f.ContainsEnvironment(i.Environment) {
			continue
		}
		if !f.ContainsSeverity(i.Severity) {
			continue
		}
		t := parseDate(i.Timestamp)
		if !f.InDateRange(t) {
			continue
		}
		filtered = append(filtered, i)
	}

	if len(filtered) == 0 {
		return IncidentSeverity{
			MTTRBySeverity: make(map[string]float64),
		}
	}

	order := []string{"sev1", "sev2", "sev3", "sev4"}
	
	counts := make(map[string]int)
	mttrSum := make(map[string]int)
	
	for _, i := range filtered {
		counts[i.Severity]++
		mttrSum[i.Severity] += i.MttrMins
	}

	var presentSeverities []string
	countList := make([]int, 0)
	mttrMap := make(map[string]float64)

	for _, sev := range order {
		if c, ok := counts[sev]; ok && c > 0 {
			presentSeverities = append(presentSeverities, sev)
			countList = append(countList, c)
			mttrMap[sev] = float64(mttrSum[sev]) / float64(c)
		}
	}

	return IncidentSeverity{
		Severities:     presentSeverities,
		Counts:         countList,
		MTTRBySeverity: mttrMap,
	}
}
