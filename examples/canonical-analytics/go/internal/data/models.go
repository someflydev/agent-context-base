package data

type Event struct {
	ID          string `json:"id"`
	Timestamp   string `json:"timestamp"`
	Environment string `json:"environment"`
	Service     string `json:"service"`
	Count       int    `json:"count"`
}

type Session struct {
	ID          string `json:"id"`
	DurationMs  int    `json:"duration_ms"`
	Environment string `json:"environment"`
	FunnelStage string `json:"funnel_stage"`
}

type Service struct {
	Name        string  `json:"name"`
	Environment string  `json:"environment"`
	ErrorRate   float64 `json:"error_rate"`
}

type Deployment struct {
	ID          string `json:"id"`
	Timestamp   string `json:"timestamp"`
	Service     string `json:"service"`
	Environment string `json:"environment"`
	Status      string `json:"status"`
}

type Incident struct {
	ID          string `json:"id"`
	Timestamp   string `json:"timestamp"`
	Severity    string `json:"severity"`
	MttrMins    int    `json:"mttr_mins"`
	Service     string `json:"service"`
	Environment string `json:"environment"`
}

type LatencySample struct {
	ID          string  `json:"id"`
	Timestamp   string  `json:"timestamp"`
	LatencyMs   float64 `json:"latency_ms"`
	Service     string  `json:"service"`
	Environment string  `json:"environment"`
}

type FunnelStage struct {
	StageName   string  `json:"stage_name"`
	Environment string  `json:"environment"`
	DropOffRate float64 `json:"drop_off_rate"`
}
