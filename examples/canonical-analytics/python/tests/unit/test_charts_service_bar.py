from src.analytics_workbench.charts.service_bar import build_service_bar_figure
from src.analytics_workbench.analytics.services import ServiceErrorRates

def test_with_valid_aggregate():
    agg = ServiceErrorRates(services=["api"], error_rates=[0.05], total_events=[100])
    fig = build_service_bar_figure(agg)
    assert len(fig["data"]) >= 1

def test_axis_titles_set():
    agg = ServiceErrorRates(services=["api"], error_rates=[0.05], total_events=[100])
    fig = build_service_bar_figure(agg)
    assert fig["layout"]["xaxis"]["title"]["text"]
    assert fig["layout"]["yaxis"]["title"]["text"]

def test_hovertemplate_set():
    agg = ServiceErrorRates(services=["api"], error_rates=[0.05], total_events=[100])
    fig = build_service_bar_figure(agg)
    for trace in fig["data"]:
        assert trace["hovertemplate"]

def test_with_empty_aggregate():
    agg = ServiceErrorRates(services=[], error_rates=[], total_events=[])
    fig = build_service_bar_figure(agg)
    assert fig is not None

def test_meta_key_present():
    agg = ServiceErrorRates(services=["api"], error_rates=[0.05], total_events=[100])
    fig = build_service_bar_figure(agg)
    assert "total_count" in fig["meta"]
