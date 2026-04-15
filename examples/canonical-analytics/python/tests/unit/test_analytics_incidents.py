from src.analytics_workbench.analytics.incidents import aggregate_incident_severity, IncidentSeverity
from src.analytics_workbench.data.loader import get_dataset
from src.analytics_workbench.filters import FilterState

def test_with_smoke_fixture():
    dataset = get_dataset()
    agg = aggregate_incident_severity(dataset.incidents, FilterState())
    assert isinstance(agg, IncidentSeverity)

def test_with_empty_input():
    agg = aggregate_incident_severity([], FilterState())
    assert isinstance(agg, IncidentSeverity)

def test_filter_by_service():
    dataset = get_dataset()
    agg = aggregate_incident_severity(dataset.incidents, FilterState(services=["billing-api"]))
    assert isinstance(agg, IncidentSeverity)

def test_filter_by_environment():
    dataset = get_dataset()
    agg = aggregate_incident_severity(dataset.incidents, FilterState(environment=["production"]))
    assert isinstance(agg, IncidentSeverity)
