defmodule Taskflow.CoreTest do
  use ExUnit.Case, async: true

  alias Taskflow.Core.{Filter, Loader, Stats}

  @fixtures Path.expand("../../../fixtures", __DIR__)

  test "loads shared fixture jobs" do
    jobs = Loader.load_jobs(@fixtures)
    assert length(jobs) == 20
    assert hd(jobs).id == "job-001"
  end

  test "filters by status" do
    jobs = Loader.load_jobs(@fixtures)
    filtered = Filter.filter(jobs, status: "done")
    assert Enum.all?(filtered, &(&1.status == "done"))
  end

  test "computes stats" do
    stats = @fixtures |> Loader.load_jobs() |> Stats.compute()
    assert stats.total == 20
    assert stats.by_status["failed"] == 4
  end
end
