defmodule Taskflow.Core.Filter do
  def filter(jobs, opts \\ []) do
    jobs
    |> filter_status(Keyword.get(opts, :status))
    |> filter_tag(Keyword.get(opts, :tag))
  end

  def sort(jobs, :name), do: Enum.sort_by(jobs, & &1.name)
  def sort(jobs, :status), do: Enum.sort_by(jobs, &{&1.status, &1.name})
  def sort(jobs, _) do
    Enum.sort_by(jobs, &{&1.started_at || ~U[1970-01-01 00:00:00Z], &1.name}, :desc)
  end

  defp filter_status(jobs, nil), do: jobs
  defp filter_status(jobs, ""), do: jobs
  defp filter_status(jobs, status), do: Enum.filter(jobs, &(&1.status == status))

  defp filter_tag(jobs, nil), do: jobs
  defp filter_tag(jobs, ""), do: jobs
  defp filter_tag(jobs, tag), do: Enum.filter(jobs, &(tag in &1.tags))
end
