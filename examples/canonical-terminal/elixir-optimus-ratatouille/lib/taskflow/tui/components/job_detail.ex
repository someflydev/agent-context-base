defmodule Taskflow.Tui.Components.JobDetail do
  import Ratatouille.View

  def render(nil) do
    panel title: "Detail" do
      label(content: "No job selected")
    end
  end

  def render(job) do
    panel title: "Detail" do
      [
        label(content: "ID: #{job.id}"),
        label(content: "Status: #{job.status}"),
        label(content: "Started: #{format_time(job.started_at)}"),
        label(content: "Tags: #{Enum.join(job.tags, ", ")}"),
        label(content: "Output:"),
        Enum.map(job.output_lines, &label(content: "  - #{&1}"))
      ]
    end
  end

  defp format_time(nil), do: "-"
  defp format_time(value), do: DateTime.to_iso8601(value)
end
