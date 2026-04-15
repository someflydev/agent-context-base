from dataclasses import dataclass
from ..data.models import Incident, Service
from ..filters import FilterState

@dataclass
class IncidentSeverity:
    severities: list[str]
    counts: list[int]
    mttr_by_severity: dict[str, float]

def aggregate_incident_severity(incidents: list[Incident], filters: FilterState, services: list[Service] = None) -> IncidentSeverity:
    import pandas as pd
    
    if services is None:
        from ..data.loader import get_dataset
        services = get_dataset().services
    
    valid_services = {s.name for s in services}
    
    filtered = []
    for i in incidents:
        d = i.timestamp[:10]
        if filters.date_from and d < filters.date_from.isoformat(): continue
        if filters.date_to and d > filters.date_to.isoformat(): continue
        if filters.environment and i.environment not in filters.environment: continue
        if filters.severity and i.severity not in filters.severity: continue
        
        if i.service not in valid_services: continue
        if filters.services and i.service not in filters.services: continue
        
        filtered.append({
            "severity": i.severity,
            "mttr": i.mttr_mins
        })
        
    if not filtered:
        return IncidentSeverity(severities=[], counts=[], mttr_by_severity={})
        
    df = pd.DataFrame(filtered)
    
    # Order severities
    order = ["critical", "high", "medium", "low"]
    
    agg = df.groupby("severity").agg(
        count=("severity", "count"),
        mttr=("mttr", "mean")
    )
    
    # reindex
    present_order = [s for s in order if s in agg.index]
    agg = agg.loc[present_order]
    
    mttr_dict = {row.Index: float(row.mttr) if pd.notna(row.mttr) else 0.0 for row in agg.itertuples()}
    
    return IncidentSeverity(
        severities=agg.index.tolist(),
        counts=agg["count"].tolist(),
        mttr_by_severity=mttr_dict
    )
