package charts

import (
	"time"

	"analytics-workbench-go/internal/analytics"
)

func BuildIncidentBarFigure(agg analytics.IncidentSeverity) PlotlyFigure {
	now := time.Now().UTC().Format(time.RFC3339)

	if len(agg.Severities) == 0 {
		return PlotlyFigure{
			Data: []PlotlyTrace{{
				Type:          "bar",
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

	trace := PlotlyTrace{
		Type:          "bar",
		Name:          "Incidents",
		X:             agg.Severities,
		Y:             agg.Counts,
		HoverTemplate: "Severity %{x}: %{y} incidents<extra></extra>",
		Marker: &PlotlyMarker{
			Color: []string{"#ef4444", "#f97316", "#eab308", "#3b82f6"}, // dynamic colors per bar if possible
		},
	}

	var total int
	for _, c := range agg.Counts {
		total += c
	}

	return PlotlyFigure{
		Data: []PlotlyTrace{trace},
		Layout: PlotlyLayout{
			Title: PlotlyTitle{Text: "Incident Distribution by Severity"},
			XAxis: PlotlyAxis{Title: PlotlyAxisTitle{Text: "Severity"}},
			YAxis: PlotlyAxis{Title: PlotlyAxisTitle{Text: "Count"}},
		},
		Meta: PlotlyMeta{
			TotalCount:  total,
			GeneratedAt: now,
		},
	}
}
