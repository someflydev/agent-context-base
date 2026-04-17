use super::{match_date, match_multi, EventHeatmap};
use crate::data::models::Event;
use crate::filters::FilterState;
use chrono::{DateTime, Datelike, Timelike, Utc};

pub fn aggregate_event_heatmap(events: &[Event], filters: &FilterState) -> EventHeatmap {
    let days_order = vec![
        "Mon".to_string(),
        "Tue".to_string(),
        "Wed".to_string(),
        "Thu".to_string(),
        "Fri".to_string(),
        "Sat".to_string(),
        "Sun".to_string(),
    ];
    let hours: Vec<i32> = (0..24).collect();

    let mut filtered_events = Vec::new();
    for ev in events {
        if !match_date(&ev.timestamp, &filters.date_from, &filters.date_to) {
            continue;
        }
        if !match_multi(&ev.environment, &filters.environment) {
            continue;
        }
        filtered_events.push(ev);
    }

    let mut counts = vec![vec![0; 24]; 7]; // 7 days, 24 hours

    if filtered_events.is_empty() {
        return EventHeatmap {
            hours,
            days: days_order,
            counts,
        };
    }

    for ev in filtered_events {
        if let Ok(dt) = ev.timestamp.parse::<DateTime<Utc>>() {
            let hour = dt.hour() as usize;
            let day_idx = dt.weekday().num_days_from_monday() as usize;
            counts[day_idx][hour] += ev.count;
        }
    }

    EventHeatmap {
        hours,
        days: days_order,
        counts,
    }
}
