from src.analytics_workbench.analytics.funnel import aggregate_funnel_stages, FunnelStages
from src.analytics_workbench.data.loader import get_dataset
from src.analytics_workbench.filters import FilterState

def test_with_smoke_fixture():
    dataset = get_dataset()
    agg = aggregate_funnel_stages(dataset.sessions, FilterState())
    assert isinstance(agg, FunnelStages)

def test_with_empty_input():
    agg = aggregate_funnel_stages([], FilterState())
    assert isinstance(agg, FunnelStages)

def test_filter_by_service():
    dataset = get_dataset()
    agg = aggregate_funnel_stages(dataset.sessions, FilterState(services=["billing-api"]))
    assert isinstance(agg, FunnelStages)

def test_filter_by_environment():
    dataset = get_dataset()
    agg = aggregate_funnel_stages(dataset.sessions, FilterState(environment=["production"]))
    assert isinstance(agg, FunnelStages)
