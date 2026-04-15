from dataclasses import dataclass
from ..data.models import Event, Service
from ..filters import FilterState

@dataclass
class ServiceErrorRates:
    services: list[str]
    error_rates: list[float]
    total_events: list[int]

def aggregate_service_error_rates(events: list[Event], services: list[Service], filters: FilterState) -> ServiceErrorRates:
    import pandas as pd
    
    # We use services directly, as they contain the error_rate in this domain
    filtered_services = []
    for s in services:
        if filters.environment and s.environment not in filters.environment: continue
        if filters.services and s.name not in filters.services: continue
        filtered_services.append(s)
        
    if not filtered_services:
        return ServiceErrorRates(services=[], error_rates=[], total_events=[])
        
    # Just average the error rates across environments for the same service if needed
    # or just sum total events for the service
    df_s = pd.DataFrame([{"service": s.name, "error_rate": s.error_rate} for s in filtered_services])
    
    # event counts per service
    event_counts = {}
    for e in events:
        if e.service:
            event_counts[e.service] = event_counts.get(e.service, 0) + e.count
            
    agg = df_s.groupby("service").agg(error_rate=("error_rate", "mean"))
    agg = agg.sort_values("error_rate", ascending=False)
    
    services_list = agg.index.tolist()
    rates_list = agg["error_rate"].tolist()
    totals_list = [event_counts.get(s, 0) for s in services_list]
    
    return ServiceErrorRates(
        services=services_list,
        error_rates=rates_list,
        total_events=totals_list
    )
