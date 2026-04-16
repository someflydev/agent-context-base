package charts

import (
	"time"

	"analytics-workbench-go/internal/analytics"
)

func BuildTimeSeriesFigure(agg analytics.EventCountSeries) PlotlyFigure {
	now := time.Now().UTC().Format(time.RFC3339)

	if len(agg.Dates) == 0 {
		return PlotlyFigure{
			Data: []PlotlyTrace{{
				Type:          "scatter",
				Mode:          "lines+markers",
				Name:          "empty",
				HoverTemplate: "No data",
				X:             []string{},
				Y:             []int{},
			}},
			Layout: PlotlyLayout{
				Title: PlotlyTitle{Text: "No data for selected filters"},
			},
			Meta: PlotlyMeta{
				TotalCount:  0,
				GeneratedAt: now,
			},
		}
	}

	var traces []PlotlyTrace
	for env, counts := range agg.ByEnvironment {
		traces = append(traces, PlotlyTrace{
			Type:          "scatter",
			Mode:          "lines+markers",
			Name:          env,
			X:             agg.Dates,
			Y:             counts,
			HoverTemplate: "%{x}: %{y} events<extra></extra>",
		})
	}

	var total int
	for _, c := range agg.Counts {
		total += c
	}

	return PlotlyFigure{
		Data: traces,
		Layout: PlotlyLayout{
			Title: PlotlyTitle{Text: "Event Volume Trends"},
			XAxis: PlotlyAxis{Title: PlotlyAxisTitle{Text: "Date"}},
			YAxis: PlotlyAxis{Title: PlotlyAxisTitle{Text: "Event Count"}},
		},
		Meta: PlotlyMeta{
			TotalCount:  total,
			GeneratedAt: now,
		},
	}
}
