from src.analytics_workbench.analytics.distributions import aggregate_latency_histogram, aggregate_latency_by_service, LatencyHistogram, LatencyByService
from src.analytics_workbench.data.loader import get_dataset
from src.analytics_workbench.filters import FilterState

def test_with_smoke_fixture():
    dataset = get_dataset()
    agg = aggregate_latency_histogram(dataset.latency_samples, FilterState())
    assert isinstance(agg, LatencyHistogram)
    agg2 = aggregate_latency_by_service(dataset.latency_samples, dataset.services, FilterState())
    assert isinstance(agg2, LatencyByService)

def test_with_empty_input():
    agg = aggregate_latency_histogram([], FilterState())
    assert isinstance(agg, LatencyHistogram)
    agg2 = aggregate_latency_by_service([], [], FilterState())
    assert isinstance(agg2, LatencyByService)

def test_filter_by_service():
    dataset = get_dataset()
    agg = aggregate_latency_histogram(dataset.latency_samples, FilterState(services=["billing-api"]))
    assert isinstance(agg, LatencyHistogram)

def test_filter_by_environment():
    dataset = get_dataset()
    agg = aggregate_latency_by_service(dataset.latency_samples, dataset.services, FilterState(environment=["production"]))
    assert isinstance(agg, LatencyByService)
