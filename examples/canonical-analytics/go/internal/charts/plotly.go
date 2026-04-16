package charts

import (
	"encoding/json"
)

type PlotlyMarker struct {
	Colorscale interface{} `json:"colorscale,omitempty"`
	Color      interface{} `json:"color,omitempty"`
	Line       interface{} `json:"line,omitempty"`
}

type PlotlyTrace struct {
	Type          string        `json:"type"`
	Mode          string        `json:"mode,omitempty"`
	Name          string        `json:"name"`
	X             interface{}   `json:"x,omitempty"`
	Y             interface{}   `json:"y,omitempty"`
	Z             interface{}   `json:"z,omitempty"`
	Orientation   string        `json:"orientation,omitempty"`
	HoverTemplate string        `json:"hovertemplate"`
	Marker        *PlotlyMarker `json:"marker,omitempty"`
	Text          interface{}   `json:"text,omitempty"`
	TextPosition  string        `json:"textposition,omitempty"`
	TextInfo      string        `json:"textinfo,omitempty"`
	BoxPoints     interface{}   `json:"boxpoints,omitempty"`
	Line          interface{}   `json:"line,omitempty"`
	Connector     interface{}   `json:"connector,omitempty"`
}

type PlotlyAxisTitle struct {
	Text string `json:"text"`
}

type PlotlyAxis struct {
	Title    PlotlyAxisTitle `json:"title"`
	Type     string          `json:"type,omitempty"`
	TickMode string          `json:"tickmode,omitempty"`
	ShowGrid bool            `json:"showgrid,omitempty"`
	ZeroLine bool            `json:"zeroline,omitempty"`
	CategoryOrder string     `json:"categoryorder,omitempty"`
}

type PlotlyTitle struct {
	Text string `json:"text"`
}

type PlotlyMargin struct {
	L int `json:"l,omitempty"`
	R int `json:"r,omitempty"`
	T int `json:"t,omitempty"`
	B int `json:"b,omitempty"`
}

type PlotlyLayout struct {
	Title      PlotlyTitle   `json:"title"`
	XAxis      PlotlyAxis    `json:"xaxis"`
	YAxis      PlotlyAxis    `json:"yaxis"`
	Height     int           `json:"height,omitempty"`
	Margin     *PlotlyMargin `json:"margin,omitempty"`
	Barmode    string        `json:"barmode,omitempty"`
	ShowLegend bool          `json:"showlegend,omitempty"`
	HoverMode  string        `json:"hovermode,omitempty"`
}

type PlotlyMeta struct {
	TotalCount     int      `json:"total_count"`
	FiltersApplied []string `json:"filters_applied"`
	GeneratedAt    string   `json:"generated_at"`
}

type PlotlyFigure struct {
	Data   []PlotlyTrace `json:"data"`
	Layout PlotlyLayout  `json:"layout"`
	Meta   PlotlyMeta    `json:"meta"`
}

func (f PlotlyFigure) ToJSON() ([]byte, error) {
	return json.Marshal(f)
}
