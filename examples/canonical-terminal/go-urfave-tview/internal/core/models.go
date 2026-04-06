package core

type JobStatus string

const (
	StatusPending JobStatus = "pending"
	StatusRunning JobStatus = "running"
	StatusDone    JobStatus = "done"
	StatusFailed  JobStatus = "failed"
)

type Job struct {
	ID          string    `json:"id"`
	Name        string    `json:"name"`
	Status      JobStatus `json:"status"`
	StartedAt   *string   `json:"started_at"`
	DurationS   *float64  `json:"duration_s"`
	Tags        []string  `json:"tags"`
	OutputLines []string  `json:"output_lines"`
}

type Event struct {
	EventID   string `json:"event_id"`
	JobID     string `json:"job_id"`
	EventType string `json:"event_type"`
	Timestamp string `json:"timestamp"`
	Message   string `json:"message"`
}

type Config struct {
	QueueName        string `json:"queue_name"`
	RefreshIntervalS int    `json:"refresh_interval_s"`
	MaxDisplayJobs   int    `json:"max_display_jobs"`
	DefaultOutput    string `json:"default_output"`
	FixtureMode      bool   `json:"fixture_mode"`
}

type Stats struct {
	Total        int            `json:"total"`
	ByStatus     map[string]int `json:"by_status"`
	AvgDurationS float64        `json:"avg_duration_s"`
	FailureRate  float64        `json:"failure_rate"`
}
