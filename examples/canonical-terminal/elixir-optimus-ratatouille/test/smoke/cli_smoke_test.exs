defmodule Taskflow.CliSmokeTest do
  use ExUnit.Case, async: true

  import ExUnit.CaptureIO

  alias Taskflow.CLI.Main
  alias Taskflow.CLI.Output
  alias Taskflow.Core.{Filter, Loader, Stats}

  @fixtures Path.expand("../../../fixtures", __DIR__)

  test "list table output contains markers" do
    jobs = Loader.load_jobs(@fixtures)

    output =
      capture_io(fn ->
        Output.print_jobs(jobs, :table)
      end)

    assert output =~ "## BEGIN_JOBS ##"
  end

  test "list json returns 20 items" do
    jobs = Loader.load_jobs(@fixtures)

    output =
      capture_io(fn ->
        Output.print_jobs(jobs, :json)
      end)

    assert length(Jason.decode!(output)) == 20
  end

  test "filter status returns only done jobs" do
    jobs = Loader.load_jobs(@fixtures)
    filtered = Filter.filter(jobs, status: "done")
    assert Enum.all?(filtered, &(&1.status == "done"))
  end

  test "stats compute total jobs" do
    assert (@fixtures |> Loader.load_jobs() |> Stats.compute()).total == 20
  end

  test "watch no tui returns ok" do
    assert capture_io(fn ->
             assert :ok = Main.dispatch(["watch", "--no-tui", "--fixtures-path", @fixtures])
           end) =~ "## BEGIN_JOBS ##"
  end
end
