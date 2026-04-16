package analytics

import (
	"math"
	"sort"
	"time"
)

func percentile(values []float64, p float64) float64 {
	if len(values) == 0 {
		return 0.0
	}
	if len(values) == 1 {
		return values[0]
	}
	sort.Float64s(values)
	k := (float64(len(values)-1) * p) / 100.0
	f := math.Floor(k)
	c := math.Ceil(k)
	if f == c {
		return values[int(k)]
	}
	d0 := values[int(f)] * (c - k)
	d1 := values[int(c)] * (k - f)
	return d0 + d1
}

func parseDate(ts string) time.Time {
	if len(ts) >= 10 {
		if t, err := time.Parse("2006-01-02", ts[:10]); err == nil {
			return t
		}
	}
	return time.Time{}
}

func formatHour(h int) string {
	if h < 10 {
		return "0" + string(rune('0'+h)) + ":00"
	}
	return string(rune('0'+h/10)) + string(rune('0'+h%10)) + ":00"
}
