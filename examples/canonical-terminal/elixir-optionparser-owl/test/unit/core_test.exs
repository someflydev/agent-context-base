defmodule TaskflowOwl.CoreTest do
  use ExUnit.Case, async: true

  alias Taskflow.Core.{Filter, Loader, Stats}

  @fixtures Path.expand("../../../fixtures", __DIR__)

  test "loads jobs" do
    jobs = Loader.load_jobs(@fixtures)
    assert length(jobs) == 20
  end

  test "filters failed jobs" do
    jobs = Loader.load_jobs(@fixtures)
    assert Enum.all?(Filter.filter(jobs, status: "failed"), &(&1.status == "failed"))
  end

  test "computes queue stats" do
    stats = @fixtures |> Loader.load_jobs() |> Stats.compute()
    assert stats.total == 20
    assert stats.by_status["done"] == 9
  end
end
