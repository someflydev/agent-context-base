from src.analytics_workbench.charts.latency_histogram import build_latency_histogram_figure
from src.analytics_workbench.charts.latency_boxplot import build_latency_boxplot_figure
from src.analytics_workbench.analytics.distributions import LatencyHistogram, LatencyByService

def test_with_valid_aggregate():
    agg = LatencyHistogram(values=[100.0, 200.0], bin_size=10.0, p50=150.0, p95=190.0, p99=195.0)
    fig = build_latency_histogram_figure(agg)
    assert len(fig["data"]) >= 1
    
    agg2 = LatencyByService(services=["api"], p50s=[100.0], p95s=[200.0], p99s=[300.0])
    fig2 = build_latency_boxplot_figure(agg2)
    assert len(fig2["data"]) >= 1

def test_axis_titles_set():
    agg = LatencyHistogram(values=[100.0], bin_size=10.0, p50=100.0, p95=100.0, p99=100.0)
    fig = build_latency_histogram_figure(agg)
    assert fig["layout"]["xaxis"]["title"]["text"]
    assert fig["layout"]["yaxis"]["title"]["text"]

def test_hovertemplate_set():
    agg = LatencyHistogram(values=[100.0], bin_size=10.0, p50=100.0, p95=100.0, p99=100.0)
    fig = build_latency_histogram_figure(agg)
    for trace in fig["data"]:
        assert trace["hovertemplate"]

def test_with_empty_aggregate():
    agg = LatencyHistogram(values=[], bin_size=10.0, p50=0.0, p95=0.0, p99=0.0)
    fig = build_latency_histogram_figure(agg)
    assert fig is not None

def test_meta_key_present():
    agg = LatencyHistogram(values=[100.0], bin_size=10.0, p50=100.0, p95=100.0, p99=100.0)
    fig = build_latency_histogram_figure(agg)
    assert "total_count" in fig["meta"]
