defmodule Taskflow.Core.Stats do
  @statuses ~w[pending running done failed]

  def compute(jobs) do
    counts = Enum.into(@statuses, %{}, &{&1, 0})

    {counts, durations} =
      Enum.reduce(jobs, {counts, []}, fn job, {acc, durations} ->
        {
          Map.update!(acc, job.status, &(&1 + 1)),
          if(job.duration_s, do: [job.duration_s | durations], else: durations)
        }
      end)

    total = length(jobs)

    %{
      total: total,
      by_status: counts,
      avg_duration_s:
        case durations do
          [] -> 0.0
          _ -> Float.round(Enum.sum(durations) / length(durations), 2)
        end,
      failure_rate: if(total == 0, do: 0.0, else: Float.round(Map.fetch!(counts, "failed") / total, 2))
    }
  end
end
