package charts

import (
	"time"

	"analytics-workbench-go/internal/analytics"
)

func BuildHeatmapFigure(agg analytics.EventHeatmap) PlotlyFigure {
	now := time.Now().UTC().Format(time.RFC3339)

	var hasData bool
	var total int
	for _, row := range agg.Counts {
		for _, c := range row {
			if c > 0 {
				hasData = true
			}
			total += c
		}
	}

	if !hasData {
		return PlotlyFigure{
			Data: []PlotlyTrace{{
				Type:          "heatmap",
				Name:          "empty",
				HoverTemplate: "No data",
				X:             []int{},
				Y:             []string{},
				Z:             [][]int{},
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

	// Heatmap wants X as hours, Y as days, Z as 2D array [day][hour]
	trace := PlotlyTrace{
		Type:          "heatmap",
		Name:          "Density",
		X:             agg.Hours,
		Y:             agg.Days,
		Z:             agg.Counts,
		HoverTemplate: "%{y} at %{x}h: %{z} events<extra></extra>",
		Marker: &PlotlyMarker{
			Colorscale: "Blues",
		},
	}

	return PlotlyFigure{
		Data: []PlotlyTrace{trace},
		Layout: PlotlyLayout{
			Title: PlotlyTitle{Text: "Event Heatmap"},
			XAxis: PlotlyAxis{Title: PlotlyAxisTitle{Text: "Hour of Day"}, TickMode: "linear"},
			YAxis: PlotlyAxis{Title: PlotlyAxisTitle{Text: "Day of Week"}, CategoryOrder: "array"}, // category order handles correctly by default if Y given in order
		},
		Meta: PlotlyMeta{
			TotalCount:  total,
			GeneratedAt: now,
		},
	}
}
