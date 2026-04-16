package charts

import (
	"time"

	"analytics-workbench-go/internal/analytics"
)

func BuildLatencyHistogramFigure(agg analytics.LatencyHistogram) PlotlyFigure {
	now := time.Now().UTC().Format(time.RFC3339)

	if len(agg.Values) == 0 {
		return PlotlyFigure{
			Data: []PlotlyTrace{{
				Type:          "histogram",
				Name:          "empty",
				HoverTemplate: "No data",
				X:             []float64{},
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
		Type:          "histogram",
		Name:          "Latency",
		X:             agg.Values,
		HoverTemplate: "Latency: %{x}ms<br>Count: %{y}<extra></extra>",
		Marker: &PlotlyMarker{
			Color: "#3b82f6", // blue-500
		},
	}

	return PlotlyFigure{
		Data: []PlotlyTrace{trace},
		Layout: PlotlyLayout{
			Title: PlotlyTitle{Text: "Latency Distribution"},
			XAxis: PlotlyAxis{Title: PlotlyAxisTitle{Text: "Latency (ms)"}},
			YAxis: PlotlyAxis{Title: PlotlyAxisTitle{Text: "Count"}},
		},
		Meta: PlotlyMeta{
			TotalCount:  len(agg.Values),
			GeneratedAt: now,
		},
	}
}
