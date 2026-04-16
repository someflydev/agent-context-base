package analytics

import (
	"analytics-workbench-go/internal/data"
	"analytics-workbench-go/internal/filters"
)

type FunnelStages struct {
	Stages       []string
	Counts       []int
	DropOffRates []float64
}

func AggregateFunnel(sessions []data.Session, stages []data.FunnelStage, f filters.FilterState) FunnelStages {
	var filtered []data.Session
	for _, s := range sessions {
		if !f.ContainsEnvironment(s.Environment) {
			continue
		}
		filtered = append(filtered, s)
	}

	stageNames := make([]string, len(stages))
	orderMap := make(map[string]int)
	for i, s := range stages {
		stageNames[i] = s.StageName
		orderMap[s.StageName] = i
	}

	if len(filtered) == 0 {
		return FunnelStages{
			Stages:       stageNames,
			Counts:       make([]int, len(stageNames)),
			DropOffRates: make([]float64, len(stageNames)),
		}
	}

	counts := make(map[string]int)
	for _, s := range filtered {
		finalOrder, ok := orderMap[s.FunnelStage]
		if !ok {
			finalOrder = -1
		}
		for _, stage := range stageNames {
			if finalOrder >= orderMap[stage] {
				counts[stage]++
			}
		}
	}

	stageCounts := make([]int, len(stageNames))
	dropOffs := make([]float64, len(stageNames))

	for i, name := range stageNames {
		stageCounts[i] = counts[name]
		if i == 0 || stageCounts[i-1] == 0 {
			dropOffs[i] = 0.0
		} else {
			dropOffs[i] = 1.0 - (float64(stageCounts[i]) / float64(stageCounts[i-1]))
		}
	}

	return FunnelStages{
		Stages:       stageNames,
		Counts:       stageCounts,
		DropOffRates: dropOffs,
	}
}
