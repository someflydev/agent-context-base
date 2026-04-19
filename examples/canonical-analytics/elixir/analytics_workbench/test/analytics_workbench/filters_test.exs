defmodule AnalyticsWorkbench.FiltersTest do
  use ExUnit.Case, async: true
  alias AnalyticsWorkbench.Filters

  test "parse empty params returns zero-value FilterState" do
    assert %Filters{services: [], environment: [], severity: [], date_from: nil, date_to: nil} = Filters.parse(%{})
  end

  test "parse multi-value services" do
    params = %{"services" => ["auth", "billing"]}
    assert Filters.parse(params).services == ["auth", "billing"]
  end

  test "parse comma-separated services" do
    params = %{"services" => "auth,billing"}
    assert Filters.parse(params).services == ["auth", "billing"]
  end

  test "parse date range" do
    params = %{"date_from" => "2023-01-01", "date_to" => "2023-01-31"}
    filters = Filters.parse(params)
    assert filters.date_from == "2023-01-01"
    assert filters.date_to == "2023-01-31"
  end
end
