defmodule Taskflow.Core.Loader do
  alias Taskflow.Core.Job

  defmodule FixtureError do
    defexception [:message]
  end

  def default_fixtures_path do
    System.get_env("TASKFLOW_FIXTURES_PATH") ||
      Path.expand("../../../../fixtures", __DIR__)
  end

  def load_jobs(path \\ default_fixtures_path()) do
    path
    |> load_json("jobs.json")
    |> Enum.map(&Job.from_map/1)
  end

  def load_config(path \\ default_fixtures_path()) do
    load_json(path, "config.json")
  end

  defp load_json(path, filename) do
    fixtures_path = Path.expand(path)

    unless File.dir?(fixtures_path) do
      raise FixtureError, "fixtures path does not exist: #{fixtures_path}"
    end

    target = Path.join(fixtures_path, filename)

    unless File.exists?(target) do
      raise FixtureError, "missing fixture file: #{target}"
    end

    decode_json(target)
  end

  defp decode_json(target) do
    target
    |> File.read!()
    |> Jason.decode!()
  rescue
    e in Jason.DecodeError -> raise FixtureError, "invalid json in #{target}: #{Exception.message(e)}"
  end
end
