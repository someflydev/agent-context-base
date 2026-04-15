import json
import os
from .models import Event, Session, Service, Deployment, Incident, LatencySample, FunnelStage
from ..config import FIXTURE_PATH

_DATASET_CACHE = None

def get_fixture_path() -> str:
    if FIXTURE_PATH and os.path.exists(FIXTURE_PATH):
        return FIXTURE_PATH
    # Default relative to this file: examples/canonical-analytics/domain/fixtures/smoke.json
    # loader.py is in examples/canonical-analytics/python/src/analytics_workbench/data/
    # root is 6 levels up? No, domain/fixtures is sibling to python/
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
    return os.path.join(base_dir, "domain", "fixtures", "smoke.json")

from dataclasses import dataclass

@dataclass
class Dataset:
    events: list[Event]
    sessions: list[Session]
    services: list[Service]
    deployments: list[Deployment]
    incidents: list[Incident]
    latency_samples: list[LatencySample]
    funnel_stages: list[FunnelStage]

def load_dataset() -> Dataset:
    path = get_fixture_path()
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return Dataset(
        events=[Event.from_dict(d) for d in data.get("events", [])],
        sessions=[Session.from_dict(d) for d in data.get("sessions", [])],
        services=[Service.from_dict(d) for d in data.get("services", [])],
        deployments=[Deployment.from_dict(d) for d in data.get("deployments", [])],
        incidents=[Incident.from_dict(d) for d in data.get("incidents", [])],
        latency_samples=[LatencySample.from_dict(d) for d in data.get("latency_samples", [])],
        funnel_stages=[FunnelStage.from_dict(d) for d in data.get("funnel_stages", [])],
    )

def get_dataset() -> Dataset:
    global _DATASET_CACHE
    if _DATASET_CACHE is None:
        _DATASET_CACHE = load_dataset()
    return _DATASET_CACHE
