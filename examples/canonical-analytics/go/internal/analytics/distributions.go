package analytics

import (
	"sort"

	"analytics-workbench-go/internal/data"
	"analytics-workbench-go/internal/filters"
)

type LatencyHistogram struct {
	Values []float64
	P50    float64
	P95    float64
	P99    float64
}

type LatencyByService struct {
	Services []string
	P50s     []float64
	P95s     []float64
	P99s     []float64
}

func filterSamples(samples []data.LatencySample, services []data.Service, f filters.FilterState) []data.LatencySample {
	validServices := make(map[string]bool)
	if len(services) > 0 {
		for _, s := range services {
			validServices[s.Name] = true
		}
	} else {
		for _, s := range samples {
			validServices[s.Service] = true
		}
	}

	var filtered []data.LatencySample
	for _, s := range samples {
		if !validServices[s.Service] {
			continue
		}
		if !f.ContainsService(s.Service) {
			continue
		}
		t := parseDate(s.Timestamp)
		if !f.InDateRange(t) {
			continue
		}
		// Notice: Python doesn't filter environment in latency? Python code does not apply env filter in _filter_samples.
		filtered = append(filtered, s)
	}
	return filtered
}

func AggregateLatencyHistogram(samples []data.LatencySample, services []data.Service, f filters.FilterState) LatencyHistogram {
	filtered := filterSamples(samples, services, f)
	if len(filtered) == 0 {
		return LatencyHistogram{}
	}

	values := make([]float64, len(filtered))
	for i, s := range filtered {
		values[i] = s.LatencyMs
	}

	// copy values to compute percentiles since percentile sorts in place
	vCopy := append([]float64(nil), values...)
	
	return LatencyHistogram{
		Values: values,
		P50:    percentile(vCopy, 50),
		P95:    percentile(vCopy, 95),
		P99:    percentile(vCopy, 99),
	}
}

func AggregateLatencyByService(samples []data.LatencySample, services []data.Service, f filters.FilterState) LatencyByService {
	filtered := filterSamples(samples, services, f)
	if len(filtered) == 0 {
		return LatencyByService{}
	}

	bySrv := make(map[string][]float64)
	for _, s := range filtered {
		bySrv[s.Service] = append(bySrv[s.Service], s.LatencyMs)
	}

	type srvP struct {
		Name string
		P50  float64
		P95  float64
		P99  float64
	}

	var srvs []srvP
	for name, vals := range bySrv {
		srvs = append(srvs, srvP{
			Name: name,
			P50:  percentile(append([]float64(nil), vals...), 50),
			P95:  percentile(append([]float64(nil), vals...), 95),
			P99:  percentile(append([]float64(nil), vals...), 99),
		})
	}

	sort.Slice(srvs, func(i, j int) bool {
		return srvs[i].P50 > srvs[j].P50
	})

	res := LatencyByService{
		Services: make([]string, len(srvs)),
		P50s:     make([]float64, len(srvs)),
		P95s:     make([]float64, len(srvs)),
		P99s:     make([]float64, len(srvs)),
	}

	for i, s := range srvs {
		res.Services[i] = s.Name
		res.P50s[i] = s.P50
		res.P95s[i] = s.P95
		res.P99s[i] = s.P99
	}

	return res
}
