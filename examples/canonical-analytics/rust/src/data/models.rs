use serde::Deserialize;

#[derive(Debug, Clone, Deserialize)]
pub struct Event {
    pub id: String,
    pub timestamp: String,
    pub environment: String,
    pub service: String,
    pub count: i64,
}

#[derive(Debug, Clone, Deserialize)]
pub struct Session {
    pub id: String,
    pub duration_ms: i64,
    pub environment: String,
    pub funnel_stage: String,
}

#[derive(Debug, Clone, Deserialize)]
pub struct Service {
    pub name: String,
    pub environment: String,
    pub error_rate: f64,
}

#[derive(Debug, Clone, Deserialize)]
pub struct Deployment {
    pub id: String,
    pub timestamp: String,
    pub service: String,
    pub environment: String,
    pub status: String,
}

#[derive(Debug, Clone, Deserialize)]
pub struct Incident {
    pub id: String,
    pub timestamp: String,
    pub severity: String,
    pub mttr_mins: f64,
    pub service: String,
    pub environment: String,
}

#[derive(Debug, Clone, Deserialize)]
pub struct LatencySample {
    pub id: String,
    pub timestamp: String,
    pub latency_ms: f64,
    pub service: String,
    pub environment: String,
}

#[derive(Debug, Clone, Deserialize)]
pub struct FunnelStage {
    pub stage_name: String,
    pub environment: String,
    pub drop_off_rate: f64,
}
