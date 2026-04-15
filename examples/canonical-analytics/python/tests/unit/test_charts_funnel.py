from src.analytics_workbench.charts.funnel_chart import build_funnel_figure
from src.analytics_workbench.analytics.funnel import FunnelStages

def test_with_valid_aggregate():
    agg = FunnelStages(stages=["A", "B"], counts=[100, 50], drop_off_rates=[0.0, 0.5])
    fig = build_funnel_figure(agg)
    assert len(fig["data"]) >= 1

def test_axis_titles_set():
    agg = FunnelStages(stages=["A", "B"], counts=[100, 50], drop_off_rates=[0.0, 0.5])
    fig = build_funnel_figure(agg)
    assert fig["layout"]["xaxis"]["title"]["text"]
    assert fig["layout"]["yaxis"]["title"]["text"]

def test_hovertemplate_set():
    agg = FunnelStages(stages=["A", "B"], counts=[100, 50], drop_off_rates=[0.0, 0.5])
    fig = build_funnel_figure(agg)
    for trace in fig["data"]:
        assert trace["hovertemplate"]

def test_with_empty_aggregate():
    agg = FunnelStages(stages=[], counts=[], drop_off_rates=[])
    fig = build_funnel_figure(agg)
    assert fig is not None

def test_meta_key_present():
    agg = FunnelStages(stages=["A", "B"], counts=[100, 50], drop_off_rates=[0.0, 0.5])
    fig = build_funnel_figure(agg)
    assert "total_count" in fig["meta"]
