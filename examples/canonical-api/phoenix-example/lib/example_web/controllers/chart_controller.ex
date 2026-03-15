defmodule ExampleWeb.ChartController do
  use ExampleWeb, :controller

  alias Example.Reporting

  def show(conn, %{"metric" => metric}) do
    points = Reporting.series_for(metric)
    series = [%{name: metric, points: points}]
    json(conn, %{metric: metric, series: series})
  end
end
