defmodule AnalyticsWorkbenchWeb.SmokeTest do
  use AnalyticsWorkbenchWeb.ConnCase, async: true

  test "GET / returns 200", %{conn: conn} do
    conn = get(conn, ~p"/")
    assert html_response(conn, 200) =~ "Analytics Workbench"
  end

  test "GET /trends returns 200", %{conn: conn} do
    conn = get(conn, ~p"/trends")
    assert html_response(conn, 200) =~ "Trends"
  end

  test "GET /services returns 200", %{conn: conn} do
    conn = get(conn, ~p"/services")
    assert html_response(conn, 200) =~ "Services"
  end

  test "GET /distributions returns 200", %{conn: conn} do
    conn = get(conn, ~p"/distributions")
    assert html_response(conn, 200) =~ "Distributions"
  end

  test "GET /heatmap returns 200", %{conn: conn} do
    conn = get(conn, ~p"/heatmap")
    assert html_response(conn, 200) =~ "Heatmap"
  end

  test "GET /funnel returns 200", %{conn: conn} do
    conn = get(conn, ~p"/funnel")
    assert html_response(conn, 200) =~ "Funnel"
  end

  test "GET /incidents returns 200", %{conn: conn} do
    conn = get(conn, ~p"/incidents")
    assert html_response(conn, 200) =~ "Incidents"
  end

  test "GET /api/health returns 200 with status ok", %{conn: conn} do
    conn = get(conn, ~p"/api/health")
    assert json_response(conn, 200) == %{"status" => "ok"}
  end

  test "GET /fragments/chart?view=trends returns 200", %{conn: conn} do
    conn = get(conn, ~p"/fragments/chart?view=trends")
    assert html_response(conn, 200) =~ "chart-panel"
  end

  test "GET /fragments/summary?view=trends returns 200", %{conn: conn} do
    conn = get(conn, ~p"/fragments/summary?view=trends")
    assert html_response(conn, 200) =~ "Summary"
  end

  test "GET /trends?environment[]=production returns 200", %{conn: conn} do
    conn = get(conn, ~p"/trends?environment[]=production")
    assert html_response(conn, 200) =~ "Trends"
  end
end
