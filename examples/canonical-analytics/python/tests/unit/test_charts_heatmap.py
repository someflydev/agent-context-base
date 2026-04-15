from src.analytics_workbench.charts.heatmap_chart import build_heatmap_figure
from src.analytics_workbench.analytics.heatmap import EventHeatmap

def test_with_valid_aggregate():
    agg = EventHeatmap(hours=[0], days=["Mon"], counts=[[5]])
    fig = build_heatmap_figure(agg)
    assert len(fig["data"]) >= 1

def test_axis_titles_set():
    agg = EventHeatmap(hours=[0], days=["Mon"], counts=[[5]])
    fig = build_heatmap_figure(agg)
    assert fig["layout"]["xaxis"]["title"]["text"]
    assert fig["layout"]["yaxis"]["title"]["text"]

def test_hovertemplate_set():
    agg = EventHeatmap(hours=[0], days=["Mon"], counts=[[5]])
    fig = build_heatmap_figure(agg)
    for trace in fig["data"]:
        assert trace["hovertemplate"]

def test_with_empty_aggregate():
    agg = EventHeatmap(hours=[], days=[], counts=[])
    fig = build_heatmap_figure(agg)
    assert fig is not None

def test_meta_key_present():
    agg = EventHeatmap(hours=[0], days=["Mon"], counts=[[5]])
    fig = build_heatmap_figure(agg)
    assert "total_count" in fig["meta"]
