defmodule Taskflow.CLI.Output do
  alias Taskflow.Core.Job

  def print_jobs(jobs, :json), do: IO.puts(Jason.encode_to_iodata!(Enum.map(jobs, &Job.to_map/1), pretty: true))
  def print_jobs(jobs, _format), do: marker_block("## BEGIN_JOBS ##", jobs_table(jobs), "## END_JOBS ##")

  def print_job(job, :json), do: IO.puts(Jason.encode_to_iodata!(Job.to_map(job), pretty: true))
  def print_job(job, _format), do: marker_block("## BEGIN_JOB_DETAIL ##", job_plain(job), "## END_JOB_DETAIL ##")

  def print_stats(stats, :json), do: IO.puts(Jason.encode_to_iodata!(stats, pretty: true))
  def print_stats(stats, _format), do: marker_block("## BEGIN_STATS ##", stats_plain(stats), "## END_STATS ##")

  def print_error(message), do: marker_block("## BEGIN_ERROR ##", message, "## END_ERROR ##")

  def marker_block(begin_marker, content, end_marker) do
    IO.puts(begin_marker)
    if content != "", do: IO.puts(content)
    IO.puts(end_marker)
  end

  def jobs_table(jobs) do
    header = String.pad_trailing("ID", 8) <> " " <> String.pad_trailing("NAME", 24) <> " " <>
      String.pad_trailing("STATUS", 8) <> " " <> String.pad_trailing("STARTED_AT", 20) <> " TAGS"

    rows =
      Enum.map(jobs, fn job ->
        String.pad_trailing(job.id, 8) <> " " <>
          String.pad_trailing(job.name, 24) <> " " <>
          String.pad_trailing(job.status, 8) <> " " <>
          String.pad_trailing(format_time(job.started_at), 20) <> " " <>
          Enum.join(job.tags, ",")
      end)

    Enum.join([header | rows], "\n")
  end

  def job_plain(job) do
    [
      "ID: #{job.id}",
      "Name: #{job.name}",
      "Status: #{job.status}",
      "Started: #{format_time(job.started_at)}",
      "Duration (s): #{job.duration_s || "-"}",
      "Tags: #{Enum.join(job.tags, ", ")}",
      "Output:"
      | Enum.map(job.output_lines, &"  - #{&1}")
    ]
    |> Enum.join("\n")
  end

  def stats_plain(stats) do
    [
      "Total jobs: #{stats.total}",
      "Done: #{stats.by_status["done"]}",
      "Failed: #{stats.by_status["failed"]}",
      "Running: #{stats.by_status["running"]}",
      "Pending: #{stats.by_status["pending"]}",
      "Average duration (s): #{stats.avg_duration_s}",
      "Failure rate: #{stats.failure_rate}"
    ]
    |> Enum.join("\n")
  end

  defp format_time(nil), do: "-"
  defp format_time(value), do: DateTime.to_iso8601(value)
end
