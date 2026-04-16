package charts

import (
	"time"

	"analytics-workbench-go/internal/analytics"
)

func BuildFunnelFigure(agg analytics.FunnelStages) PlotlyFigure {
	now := time.Now().UTC().Format(time.RFC3339)

	if len(agg.Stages) == 0 || agg.Counts[0] == 0 {
		return PlotlyFigure{
			Data: []PlotlyTrace{{
				Type:          "funnel",
				Name:          "empty",
				HoverTemplate: "No data",
				Y:             []string{},
				X:             []int{},
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
		Type:          "funnel",
		Name:          "Conversion",
		Y:             agg.Stages,
		X:             agg.Counts,
		TextInfo:      "value+percent initial",
		HoverTemplate: "Stage: %{y}<br>Users: %{x}<extra></extra>",
	}

	return PlotlyFigure{
		Data: []PlotlyTrace{trace},
		Layout: PlotlyLayout{
			Title: PlotlyTitle{Text: "Session Funnel"},
			// XAxis and YAxis usually not titled in Plotly funnel
		},
		Meta: PlotlyMeta{
			TotalCount:  agg.Counts[0],
			GeneratedAt: now,
		},
	}
}
