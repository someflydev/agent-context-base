defmodule TaskflowOwl.CliSmokeTest do
  use ExUnit.Case, async: true

  import ExUnit.CaptureIO

  alias Taskflow.CLI

  @fixtures Path.expand("../../../fixtures", __DIR__)

  test "list table output contains markers" do
    output = capture_io(fn -> assert :ok = CLI.dispatch(["list", "--fixtures-path", @fixtures]) end)
    assert output =~ "## BEGIN_JOBS ##"
  end

  test "list json returns 20 items" do
    output =
      capture_io(fn ->
        assert :ok = CLI.dispatch(["list", "--output", "json", "--fixtures-path", @fixtures])
      end)

    assert length(Jason.decode!(output)) == 20
  end

  test "inspect returns requested job" do
    output =
      capture_io(fn ->
        assert :ok = CLI.dispatch(["inspect", "job-001", "--output", "json", "--fixtures-path", @fixtures])
      end)

    assert Jason.decode!(output)["id"] == "job-001"
  end

  test "stats returns total jobs" do
    output =
      capture_io(fn ->
        assert :ok = CLI.dispatch(["stats", "--output", "json", "--fixtures-path", @fixtures])
      end)

    assert Jason.decode!(output)["total"] == 20
  end

  test "watch no tui prints once" do
    output =
      capture_io(fn ->
        assert :ok = CLI.dispatch(["watch", "--no-tui", "--fixtures-path", @fixtures])
      end)

    assert output =~ "## BEGIN_JOBS ##"
  end
end
