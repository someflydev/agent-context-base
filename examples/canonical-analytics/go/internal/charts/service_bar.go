package charts

import (
	"time"

	"analytics-workbench-go/internal/analytics"
)

func BuildServiceBarFigure(agg analytics.ServiceErrorRates) PlotlyFigure {
	now := time.Now().UTC().Format(time.RFC3339)

	if len(agg.Services) == 0 {
		return PlotlyFigure{
			Data: []PlotlyTrace{{
				Type:          "bar",
				Orientation:   "h",
				Name:          "empty",
				HoverTemplate: "No data",
				X:             []float64{},
				Y:             []string{},
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

	// Plotly horizontal bars display bottom-to-top by default, we reverse order to show highest at top
	var revServices []string
	var revRates []float64
	var revTotals []int

	for i := len(agg.Services) - 1; i >= 0; i-- {
		revServices = append(revServices, agg.Services[i])
		revRates = append(revRates, agg.ErrorRates[i])
		revTotals = append(revTotals, agg.TotalEvents[i])
	}

	trace := PlotlyTrace{
		Type:          "bar",
		Orientation:   "h",
		Name:          "Error Rate",
		X:             revRates,
		Y:             revServices,
		HoverTemplate: "%{y}: %{x:.2%}<extra></extra>",
		Marker: &PlotlyMarker{
			Color: "#ef4444", // red-500
		},
	}

	var total int
	for _, c := range agg.TotalEvents {
		total += c
	}

	return PlotlyFigure{
		Data: []PlotlyTrace{trace},
		Layout: PlotlyLayout{
			Title: PlotlyTitle{Text: "Service Error Rates"},
			XAxis: PlotlyAxis{Title: PlotlyAxisTitle{Text: "Error Rate"}},
			YAxis: PlotlyAxis{Title: PlotlyAxisTitle{Text: "Service"}},
		},
		Meta: PlotlyMeta{
			TotalCount:  total,
			GeneratedAt: now,
		},
	}
}
