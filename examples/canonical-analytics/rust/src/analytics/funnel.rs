use super::{match_multi, FunnelStages};
use crate::data::models::{FunnelStage, Session};
use crate::filters::FilterState;

pub fn aggregate_funnel_stages(
    sessions: &[Session],
    stages: &[FunnelStage],
    filters: &FilterState,
) -> FunnelStages {
    let mut stage_names = Vec::new();
    for s in stages {
        if !stage_names.contains(&s.stage_name) {
            stage_names.push(s.stage_name.clone());
        }
    }

    let mut filtered = Vec::new();
    for s in sessions {
        if !match_multi(&s.environment, &filters.environment) {
            continue;
        }
        filtered.push(s);
    }

    if filtered.is_empty() || stage_names.is_empty() {
        return FunnelStages {
            stages: stage_names.clone(),
            counts: vec![0; stage_names.len()],
            drop_off_rates: vec![0.0; stage_names.len()],
        };
    }

    let mut counts = vec![0; stage_names.len()];

    for s in filtered {
        let final_idx = stage_names.iter().position(|name| name == &s.funnel_stage).unwrap_or(usize::MAX);
        if final_idx != usize::MAX {
            for item in counts.iter_mut().take(final_idx + 1) {
                *item += 1;
            }
        }
    }

    let mut drop_off_rates = vec![0.0; stage_names.len()];
    for i in 0..counts.len() {
        if i == 0 || counts[i - 1] == 0 {
            drop_off_rates[i] = 0.0;
        } else {
            drop_off_rates[i] = 1.0 - (counts[i] as f64 / counts[i - 1] as f64);
        }
    }

    FunnelStages {
        stages: stage_names,
        counts,
        drop_off_rates,
    }
}
