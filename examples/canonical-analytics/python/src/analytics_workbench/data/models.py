from dataclasses import dataclass, field
from typing import Any, Optional

@dataclass
class Event:
    id: str
    timestamp: str
    environment: str
    service: str
    count: int

    @classmethod
    def from_dict(cls, d: dict) -> "Event":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})

@dataclass
class Session:
    id: str
    duration_ms: int
    environment: str
    funnel_stage: str

    @classmethod
    def from_dict(cls, d: dict) -> "Session":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})

@dataclass
class Service:
    name: str
    environment: str
    error_rate: float

    @classmethod
    def from_dict(cls, d: dict) -> "Service":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})

@dataclass
class Deployment:
    id: str
    timestamp: str
    service: str
    environment: str
    status: str

    @classmethod
    def from_dict(cls, d: dict) -> "Deployment":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})

@dataclass
class Incident:
    id: str
    timestamp: str
    severity: str
    mttr_mins: float
    service: str
    environment: str

    @classmethod
    def from_dict(cls, d: dict) -> "Incident":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})

@dataclass
class LatencySample:
    id: str
    timestamp: str
    latency_ms: float
    service: str
    environment: str

    @classmethod
    def from_dict(cls, d: dict) -> "LatencySample":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})

@dataclass
class FunnelStage:
    stage_name: str
    environment: str
    drop_off_rate: float

    @classmethod
    def from_dict(cls, d: dict) -> "FunnelStage":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})
