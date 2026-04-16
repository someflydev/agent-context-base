package analytics

import (
	"sort"

	"analytics-workbench-go/internal/data"
	"analytics-workbench-go/internal/filters"
)

type ServiceErrorRates struct {
	Services    []string
	ErrorRates  []float64
	TotalEvents []int
}

func AggregateServices(events []data.Event, services []data.Service, f filters.FilterState) ServiceErrorRates {
	if len(services) == 0 {
		return ServiceErrorRates{}
	}

	serviceSet := make(map[string]bool)
	rateSum := make(map[string]float64)
	rateCount := make(map[string]int)
	
	for _, s := range services {
		if !f.ContainsEnvironment(s.Environment) {
			continue
		}
		if !f.ContainsService(s.Name) {
			continue
		}
		serviceSet[s.Name] = true
		rateSum[s.Name] += s.ErrorRate
		rateCount[s.Name]++
	}

	if len(serviceSet) == 0 {
		return ServiceErrorRates{}
	}

	eventCountByService := make(map[string]int)
	for _, e := range events {
		if serviceSet[e.Service] {
			// Don't apply date filters here, the spec python logic just sums up events for valid services
			// Actually python logic doesn't apply date filters to events.
			eventCountByService[e.Service] += e.Count
		}
	}

	type srvRate struct {
		Name string
		Rate float64
	}
	var rates []srvRate
	for name := range serviceSet {
		avgRate := rateSum[name] / float64(rateCount[name])
		rates = append(rates, srvRate{Name: name, Rate: avgRate})
	}

	sort.Slice(rates, func(i, j int) bool {
		return rates[i].Rate > rates[j].Rate
	})

	res := ServiceErrorRates{
		Services:    make([]string, len(rates)),
		ErrorRates:  make([]float64, len(rates)),
		TotalEvents: make([]int, len(rates)),
	}

	for i, r := range rates {
		res.Services[i] = r.Name
		res.ErrorRates[i] = r.Rate
		res.TotalEvents[i] = eventCountByService[r.Name]
	}

	return res
}
