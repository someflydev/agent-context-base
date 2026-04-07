defmodule Taskflow.Core.Filter do
  def filter(jobs, opts \\ []) do
    jobs
    |> maybe_filter_status(Keyword.get(opts, :status))
    |> maybe_filter_tag(Keyword.get(opts, :tag))
  end

  def sort(jobs), do: Enum.sort_by(jobs, &{&1.started_at || ~U[1970-01-01 00:00:00Z], &1.name}, :desc)

  defp maybe_filter_status(jobs, nil), do: jobs
  defp maybe_filter_status(jobs, ""), do: jobs
  defp maybe_filter_status(jobs, status), do: Enum.filter(jobs, &(&1.status == status))

  defp maybe_filter_tag(jobs, nil), do: jobs
  defp maybe_filter_tag(jobs, ""), do: jobs
  defp maybe_filter_tag(jobs, tag), do: Enum.filter(jobs, &(tag in &1.tags))
end
