from src.analytics_workbench.analytics.services import aggregate_service_error_rates, ServiceErrorRates
from src.analytics_workbench.data.loader import get_dataset
from src.analytics_workbench.filters import FilterState

def test_with_smoke_fixture():
    dataset = get_dataset()
    agg = aggregate_service_error_rates(dataset.events, dataset.services, FilterState())
    assert isinstance(agg, ServiceErrorRates)

def test_with_empty_input():
    agg = aggregate_service_error_rates([], [], FilterState())
    assert isinstance(agg, ServiceErrorRates)

def test_filter_by_service():
    dataset = get_dataset()
    agg = aggregate_service_error_rates(dataset.events, dataset.services, FilterState(services=["billing-api"]))
    assert isinstance(agg, ServiceErrorRates)

def test_filter_by_environment():
    dataset = get_dataset()
    agg = aggregate_service_error_rates(dataset.events, dataset.services, FilterState(environment=["production"]))
    assert isinstance(agg, ServiceErrorRates)
