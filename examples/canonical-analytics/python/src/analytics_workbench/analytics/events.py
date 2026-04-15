from dataclasses import dataclass
from typing import List
from datetime import datetime
from ..data.models import Event
from ..filters import FilterState

@dataclass
class EventCountSeries:
    dates: list[str]
    counts: list[int]
    by_environment: dict[str, list[int]]

def aggregate_event_counts(events: list[Event], filters: FilterState) -> EventCountSeries:
    import pandas as pd
    
    # filter
    filtered = []
    for e in events:
        d = e.timestamp[:10]
        if filters.date_from and d < filters.date_from.isoformat(): continue
        if filters.date_to and d > filters.date_to.isoformat(): continue
        if filters.environment and e.environment not in filters.environment: continue
        filtered.append(e)
        
    if not filtered:
        return EventCountSeries(dates=[], counts=[], by_environment={})
        
    df = pd.DataFrame([{"date": e.timestamp[:10], "environment": e.environment, "count": e.count} for e in filtered])
    
    dates = sorted(df["date"].unique().tolist())
    by_env = {}
    
    for env in df["environment"].unique():
        env_df = df[df["environment"] == env]
        counts = env_df.groupby("date")["count"].sum().reindex(dates, fill_value=0).tolist()
        by_env[env] = counts
        
    total_counts = df.groupby("date")["count"].sum().reindex(dates, fill_value=0).tolist()
    
    return EventCountSeries(
        dates=dates,
        counts=total_counts,
        by_environment=by_env
    )
