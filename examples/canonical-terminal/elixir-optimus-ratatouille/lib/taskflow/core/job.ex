defmodule Taskflow.Core.Job do
  @enforce_keys [:id, :name, :status, :tags, :output_lines]
  defstruct [:id, :name, :status, :started_at, :duration_s, :tags, :output_lines]

  def from_map(payload) do
    %__MODULE__{
      id: Map.fetch!(payload, "id"),
      name: Map.fetch!(payload, "name"),
      status: Map.fetch!(payload, "status"),
      started_at: parse_time(Map.get(payload, "started_at")),
      duration_s: Map.get(payload, "duration_s"),
      tags: Map.get(payload, "tags", []),
      output_lines: Map.get(payload, "output_lines", [])
    }
  end

  def to_map(%__MODULE__{} = job) do
    %{
      id: job.id,
      name: job.name,
      status: job.status,
      started_at: format_time(job.started_at),
      duration_s: job.duration_s,
      tags: job.tags,
      output_lines: job.output_lines
    }
  end

  defp parse_time(nil), do: nil
  defp parse_time(value), do: DateTime.from_iso8601(value) |> elem(1)
  defp format_time(nil), do: nil
  defp format_time(value), do: DateTime.to_iso8601(value)
end

defmodule Taskflow.Core.Event do
  @enforce_keys [:event_id, :job_id, :event_type, :timestamp, :message]
  defstruct [:event_id, :job_id, :event_type, :timestamp, :message]

  def from_map(payload) do
    {:ok, timestamp, _offset} = DateTime.from_iso8601(Map.fetch!(payload, "timestamp"))

    %__MODULE__{
      event_id: Map.fetch!(payload, "event_id"),
      job_id: Map.fetch!(payload, "job_id"),
      event_type: Map.fetch!(payload, "event_type"),
      timestamp: timestamp,
      message: Map.fetch!(payload, "message")
    }
  end
end
