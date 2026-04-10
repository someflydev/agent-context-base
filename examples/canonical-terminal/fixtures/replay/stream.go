package replay

import (
	"encoding/json"
	"os"
	"sort"
	"time"
)

type Event struct {
	EventID   string `json:"event_id"`
	JobID     string `json:"job_id"`
	EventType string `json:"event_type"`
	Timestamp string `json:"timestamp"`
	Message   string `json:"message"`
}

type Job struct {
	ID          string    `json:"id"`
	Name        string    `json:"name"`
	Status      string    `json:"status"`
	StartedAt   *string   `json:"started_at"`
	DurationS   *float64  `json:"duration_s"`
	Tags        []string  `json:"tags"`
	OutputLines *[]string `json:"output_lines"`
}

type EventReplayer struct {
	events       []Event
	index        int
	current      Event
	SpeedFactor  float64
	sleepEnabled bool
}

type Option func(*EventReplayer)

func SpeedFactor(value float64) Option {
	return func(replayer *EventReplayer) {
		replayer.SpeedFactor = value
		replayer.sleepEnabled = value > 0
	}
}

func LoadEvents(eventsPath string) ([]Event, error) {
	raw, err := os.ReadFile(eventsPath)
	if err != nil {
		return nil, err
	}
	var events []Event
	if err := json.Unmarshal(raw, &events); err != nil {
		return nil, err
	}
	SortByTimestamp(events)
	return events, nil
}

func SortByTimestamp(events []Event) {
	sort.Slice(events, func(i, j int) bool {
		if events[i].Timestamp == events[j].Timestamp {
			return events[i].EventID < events[j].EventID
		}
		return events[i].Timestamp < events[j].Timestamp
	})
}

func ParseDelta(tsNew string, tsOld string) (float64, error) {
	newTime, err := time.Parse(time.RFC3339, tsNew)
	if err != nil {
		return 0, err
	}
	oldTime, err := time.Parse(time.RFC3339, tsOld)
	if err != nil {
		return 0, err
	}
	return newTime.Sub(oldTime).Seconds(), nil
}

func NewReplayer(eventsPath string, options ...Option) (*EventReplayer, error) {
	events, err := LoadEvents(eventsPath)
	if err != nil {
		return nil, err
	}
	replayer := &EventReplayer{
		events:       events,
		index:        0,
		SpeedFactor:  1.0,
		sleepEnabled: true,
	}
	for _, option := range options {
		option(replayer)
	}
	return replayer, nil
}

func (replayer *EventReplayer) Next() bool {
	if replayer.index >= len(replayer.events) {
		return false
	}
	if replayer.index > 0 && replayer.sleepEnabled {
		delta, err := ParseDelta(
			replayer.events[replayer.index].Timestamp,
			replayer.events[replayer.index-1].Timestamp,
		)
		if err == nil && delta > 0 {
			time.Sleep(time.Duration(delta/replayer.SpeedFactor*float64(time.Second)))
		}
	}
	replayer.current = replayer.events[replayer.index]
	replayer.index++
	return true
}

func (replayer *EventReplayer) Event() Event {
	return replayer.current
}
