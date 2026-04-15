from dataclasses import dataclass
from datetime import datetime
from ..data.models import Event
from ..filters import FilterState

@dataclass
class EventHeatmap:
    hours: list[int]
    days: list[str]
    counts: list[list[int]]

def aggregate_event_heatmap(events: list[Event], filters: FilterState) -> EventHeatmap:
    import pandas as pd
    import numpy as np
    
    filtered = []
    for e in events:
        d = e.timestamp[:10]
        if filters.date_from and d < filters.date_from.isoformat(): continue
        if filters.date_to and d > filters.date_to.isoformat(): continue
        if filters.environment and e.environment not in filters.environment: continue
        filtered.append(e)
        
    days_order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    hours = list(range(24))
    
    if not filtered:
        return EventHeatmap(hours=hours, days=days_order, counts=[[0]*24 for _ in range(7)])
        
    df = pd.DataFrame([{"ts": e.timestamp, "count": e.count} for e in filtered])
    df["dt"] = pd.to_datetime(df["ts"])
    df["hour"] = df["dt"].dt.hour
    df["day_idx"] = df["dt"].dt.dayofweek
    df["day"] = df["dt"].dt.strftime("%a")
    
    # groupby hour and day
    agg = df.groupby(["day", "hour"])["count"].sum().reset_index(name="count")
    
    # pivot
    pivot = agg.pivot(index="day", columns="hour", values="count").fillna(0)
    
    # reindex
    present_days = [d for d in days_order if d in pivot.index]
    pivot = pivot.reindex(days_order, fill_value=0)
    for h in hours:
        if h not in pivot.columns:
            pivot[h] = 0
    pivot = pivot[hours]
    
    return EventHeatmap(
        hours=hours,
        days=days_order,
        counts=pivot.values.tolist()
    )
