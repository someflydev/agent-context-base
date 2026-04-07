defmodule Taskflow.Tui.Components.JobList do
  import Ratatouille.View

  def render(jobs, selected) do
    panel title: "Jobs" do
      Enum.with_index(jobs)
      |> Enum.map(fn {job, index} ->
        marker = if index == selected, do: ">", else: " "
        label(content: "#{marker} #{job.id} #{job.name} [#{job.status}]")
      end)
    end
  end
end
