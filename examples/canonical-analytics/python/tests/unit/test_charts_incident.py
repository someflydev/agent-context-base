from src.analytics_workbench.charts.incident_bar import build_incident_bar_figure
from src.analytics_workbench.analytics.incidents import IncidentSeverity

def test_with_valid_aggregate():
    agg = IncidentSeverity(severities=["critical"], counts=[5], mttr_by_severity={"critical": 10.0})
    fig = build_incident_bar_figure(agg)
    assert len(fig["data"]) >= 1

def test_axis_titles_set():
    agg = IncidentSeverity(severities=["critical"], counts=[5], mttr_by_severity={"critical": 10.0})
    fig = build_incident_bar_figure(agg)
    assert fig["layout"]["xaxis"]["title"]["text"]
    assert fig["layout"]["yaxis"]["title"]["text"]

def test_hovertemplate_set():
    agg = IncidentSeverity(severities=["critical"], counts=[5], mttr_by_severity={"critical": 10.0})
    fig = build_incident_bar_figure(agg)
    for trace in fig["data"]:
        assert trace["hovertemplate"]

def test_with_empty_aggregate():
    agg = IncidentSeverity(severities=[], counts=[], mttr_by_severity={})
    fig = build_incident_bar_figure(agg)
    assert fig is not None

def test_meta_key_present():
    agg = IncidentSeverity(severities=["critical"], counts=[5], mttr_by_severity={"critical": 10.0})
    fig = build_incident_bar_figure(agg)
    assert "total_count" in fig["meta"]
