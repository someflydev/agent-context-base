from dataclasses import dataclass
from ..data.models import LatencySample, Service
from ..filters import FilterState
import numpy as np

@dataclass
class LatencyHistogram:
    values: list[float]
    bin_size: float
    p50: float
    p95: float
    p99: float

@dataclass
class LatencyByService:
    services: list[str]
    p50s: list[float]
    p95s: list[float]
    p99s: list[float]

def _filter_samples(samples: list[LatencySample], valid_services: set, filters: FilterState):
    filtered = []
    for s in samples:
        d = s.timestamp[:10]
        if filters.date_from and d < filters.date_from.isoformat(): continue
        if filters.date_to and d > filters.date_to.isoformat(): continue
        
        if s.service not in valid_services: continue
        if filters.services and s.service not in filters.services: continue
        
        filtered.append({"service": s.service, "latency_ms": s.latency_ms})
    return filtered

def aggregate_latency_histogram(samples: list[LatencySample], filters: FilterState, services: list[Service] = None) -> LatencyHistogram:
    if services is not None:
        valid_services = {s.name for s in services}
        filtered = _filter_samples(samples, valid_services, filters)
    else:
        filtered = []
        for s in samples:
            d = s.timestamp[:10]
            if filters.date_from and d < filters.date_from.isoformat(): continue
            if filters.date_to and d > filters.date_to.isoformat(): continue
            if filters.services and s.service not in filters.services: continue
            filtered.append({"service": s.service, "latency_ms": s.latency_ms})
    
    if not filtered:
        return LatencyHistogram(values=[], bin_size=10.0, p50=0.0, p95=0.0, p99=0.0)
        
    values = [f["latency_ms"] for f in filtered]
    
    return LatencyHistogram(
        values=values,
        bin_size=10.0,
        p50=float(np.percentile(values, 50)),
        p95=float(np.percentile(values, 95)),
        p99=float(np.percentile(values, 99))
    )

def aggregate_latency_by_service(samples: list[LatencySample], services: list[Service], filters: FilterState) -> LatencyByService:
    import pandas as pd
    valid_services = {s.name for s in services}
    filtered = _filter_samples(samples, valid_services, filters)
    
    if not filtered:
        return LatencyByService(services=[], p50s=[], p95s=[], p99s=[])
        
    df = pd.DataFrame(filtered)
    agg = df.groupby("service").agg(
        p50=("latency_ms", lambda x: np.percentile(x, 50)),
        p95=("latency_ms", lambda x: np.percentile(x, 95)),
        p99=("latency_ms", lambda x: np.percentile(x, 99))
    )
    agg = agg.sort_values("p50", ascending=False)
    
    return LatencyByService(
        services=agg.index.tolist(),
        p50s=agg["p50"].tolist(),
        p95s=agg["p95"].tolist(),
        p99s=agg["p99"].tolist()
    )
