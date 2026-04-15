from src.analytics_workbench.charts.time_series import build_time_series_figure
from src.analytics_workbench.analytics.events import EventCountSeries

def test_with_valid_aggregate():
    agg = EventCountSeries(dates=["2025-01-01"], counts=[10], by_environment={"production": [10]})
    fig = build_time_series_figure(agg)
    assert len(fig["data"]) >= 1

def test_axis_titles_set():
    agg = EventCountSeries(dates=["2025-01-01"], counts=[10], by_environment={"production": [10]})
    fig = build_time_series_figure(agg)
    assert fig["layout"]["xaxis"]["title"]["text"]
    assert fig["layout"]["yaxis"]["title"]["text"]

def test_hovertemplate_set():
    agg = EventCountSeries(dates=["2025-01-01"], counts=[10], by_environment={"production": [10]})
    fig = build_time_series_figure(agg)
    for trace in fig["data"]:
        assert trace["hovertemplate"]

def test_with_empty_aggregate():
    agg = EventCountSeries(dates=[], counts=[], by_environment={})
    fig = build_time_series_figure(agg)
    assert fig is not None

def test_meta_key_present():
    agg = EventCountSeries(dates=["2025-01-01"], counts=[10], by_environment={"production": [10]})
    fig = build_time_series_figure(agg)
    assert "total_count" in fig["meta"]
