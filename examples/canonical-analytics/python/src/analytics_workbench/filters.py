from dataclasses import dataclass, field
from datetime import date
from typing import Optional
from fastapi import Request

@dataclass
class FilterState:
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    services: list[str] = field(default_factory=list)
    severity: list[str] = field(default_factory=list)
    environment: list[str] = field(default_factory=list)

def _parse_multi(request: Request, key: str) -> list[str]:
    # handles repeated query params like ?services=a&services=b
    # and comma-separated like ?services=a,b
    values = request.query_params.getlist(key)
    res = []
    for v in values:
        for p in v.split(","):
            p = p.strip()
            if p:
                res.append(p)
    return res

def parse_filter_state(request: Request) -> FilterState:
    df_str = request.query_params.get("date_from")
    dt_str = request.query_params.get("date_to")
    
    date_from = date.fromisoformat(df_str) if df_str else None
    date_to = date.fromisoformat(dt_str) if dt_str else None
    
    services = _parse_multi(request, "services")
    severity = _parse_multi(request, "severity")
    environment = _parse_multi(request, "environment")
    
    return FilterState(
        date_from=date_from,
        date_to=date_to,
        services=services,
        severity=severity,
        environment=environment
    )
