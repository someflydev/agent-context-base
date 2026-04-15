from src.analytics_workbench.analytics.heatmap import aggregate_event_heatmap, EventHeatmap
from src.analytics_workbench.data.loader import get_dataset
from src.analytics_workbench.filters import FilterState

def test_with_smoke_fixture():
    dataset = get_dataset()
    agg = aggregate_event_heatmap(dataset.events, FilterState())
    assert isinstance(agg, EventHeatmap)

def test_with_empty_input():
    agg = aggregate_event_heatmap([], FilterState())
    assert isinstance(agg, EventHeatmap)

def test_filter_by_service():
    dataset = get_dataset()
    agg = aggregate_event_heatmap(dataset.events, FilterState(services=["billing-api"]))
    assert isinstance(agg, EventHeatmap)

def test_filter_by_environment():
    dataset = get_dataset()
    agg = aggregate_event_heatmap(dataset.events, FilterState(environment=["production"]))
    assert isinstance(agg, EventHeatmap)
