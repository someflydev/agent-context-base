defmodule Taskflow.Core.Loader do
  alias Taskflow.Core.{Event, Job}

  defmodule FixtureError do
    defexception [:message]
  end

  def default_fixtures_path do
    System.get_env("TASKFLOW_FIXTURES_PATH") ||
      Path.expand("../../../../fixtures", __DIR__)
  end

  def load_jobs(path \\ default_fixtures_path()) do
    load_json(path, "jobs.json", &Job.from_map/1)
  end

  def load_events(path \\ default_fixtures_path()) do
    load_json(path, "events.json", &Event.from_map/1)
    |> Enum.sort_by(& &1.timestamp, DateTime)
  end

  def load_config(path \\ default_fixtures_path()) do
    load_json(path, "config.json", & &1)
  end

  defp load_json(path, filename, mapper) do
    fixtures_path = Path.expand(path)

    unless File.dir?(fixtures_path) do
      raise FixtureError, "fixtures path does not exist: #{fixtures_path}"
    end

    target = Path.join(fixtures_path, filename)

    unless File.exists?(target) do
      raise FixtureError, "missing fixture file: #{target}"
    end

    decode_json(target, mapper)
  end

  defp decode_json(target, mapper) do
    target
    |> File.read!()
    |> Jason.decode!()
    |> then(fn
      items when is_list(items) -> Enum.map(items, mapper)
      item -> mapper.(item)
    end)
  rescue
    e in Jason.DecodeError -> raise FixtureError, "invalid json in #{target}: #{Exception.message(e)}"
  end
end
