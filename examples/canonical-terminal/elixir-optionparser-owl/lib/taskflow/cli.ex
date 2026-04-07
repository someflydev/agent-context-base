defmodule Taskflow.CLI do
  alias Taskflow.Core.{Filter, Job, Loader, Stats}

  def main(argv) do
    dispatch(argv)
    |> exit_code()
    |> System.halt()
  end

  def dispatch(argv) do
    {opts, args, _invalid} =
      OptionParser.parse(argv,
        strict: [
          status: :string,
          tag: :string,
          output: :string,
          fixtures_path: :string,
          no_tui: :boolean,
          interval: :integer
        ]
      )

    fixtures_path = Keyword.get(opts, :fixtures_path, Loader.default_fixtures_path())

    case args do
      ["list"] ->
        fixtures_path
        |> Loader.load_jobs()
        |> Filter.filter(status: Keyword.get(opts, :status), tag: Keyword.get(opts, :tag))
        |> Filter.sort()
        |> print_jobs(output_format(opts, :table))

        :ok

      ["inspect", job_id] ->
        job =
          fixtures_path
          |> Loader.load_jobs()
          |> Enum.find(&(&1.id == job_id))

        if job do
          print_job(job, output_format(opts, :plain))
          :ok
        else
          print_error("job not found: #{job_id}")
          {:error, :not_found}
        end

      ["stats"] ->
        fixtures_path
        |> Loader.load_jobs()
        |> Stats.compute()
        |> print_stats(output_format(opts, :plain))

        :ok

      ["watch"] ->
        jobs = fixtures_path |> Loader.load_jobs() |> Filter.sort()

        if Keyword.get(opts, :no_tui, false) do
          print_jobs(jobs, :table)
          :ok
        else
          watch_loop(jobs, Keyword.get(opts, :interval, 2))
        end

      _ ->
        IO.puts("taskflow <list|inspect|stats|watch> [options]")
        {:error, :invalid_args}
    end
  rescue
    e in Loader.FixtureError ->
      print_error(e.message)
      {:error, :fixture_error}
  end

  def print_jobs(jobs, :json) do
    IO.puts(Jason.encode_to_iodata!(Enum.map(jobs, &Job.to_map/1), pretty: true))
  end

  def print_jobs(jobs, _format) do
    rows =
      Enum.map(jobs, fn job ->
        %{
          id: job.id,
          name: job.name,
          status: tag_status(job.status),
          started_at: format_time(job.started_at),
          tags: Enum.join(job.tags, ",")
        }
      end)

    table =
      Owl.Table.new(rows,
        render_cell: [
          header: &to_string/1,
          body: fn
            value when is_binary(value) -> value
            value -> value
          end
        ]
      )
    marker_block("## BEGIN_JOBS ##", Owl.Data.to_chardata(table), "## END_JOBS ##")
  end

  def print_job(job, :json) do
    IO.puts(Jason.encode_to_iodata!(Job.to_map(job), pretty: true))
  end

  def print_job(job, _format) do
    marker_block(
      "## BEGIN_JOB_DETAIL ##",
      Enum.join(
        [
          "ID: #{job.id}",
          "Name: #{job.name}",
          "Status: #{job.status}",
          "Started: #{format_time(job.started_at)}",
          "Duration (s): #{job.duration_s || "-"}",
          "Tags: #{Enum.join(job.tags, ", ")}",
          "Output:"
          | Enum.map(job.output_lines, &"  - #{&1}")
        ],
        "\n"
      ),
      "## END_JOB_DETAIL ##"
    )
  end

  def print_stats(stats, :json) do
    IO.puts(Jason.encode_to_iodata!(stats, pretty: true))
  end

  def print_stats(stats, _format) do
    marker_block(
      "## BEGIN_STATS ##",
      Enum.join(
        [
          "Total jobs: #{stats.total}",
          "Done: #{stats.by_status["done"]}",
          "Failed: #{stats.by_status["failed"]}",
          "Running: #{stats.by_status["running"]}",
          "Pending: #{stats.by_status["pending"]}",
          "Average duration (s): #{stats.avg_duration_s}",
          "Failure rate: #{stats.failure_rate}"
        ],
        "\n"
      ),
      "## END_STATS ##"
    )
  end

  def print_error(message), do: marker_block("## BEGIN_ERROR ##", message, "## END_ERROR ##")

  def marker_block(begin_marker, content, end_marker) do
    IO.puts(begin_marker)
    IO.puts(content)
    IO.puts(end_marker)
  end

  def watch_loop(jobs, interval) do
    spinner = Owl.Spinner.start(label: "refreshing taskflow")
    print_jobs(jobs, :table)
    Owl.Spinner.stop(spinner)
    Process.sleep(interval * 1_000)
    :ok
  end

  defp tag_status(status) do
    case status do
      "done" -> Owl.Data.tag(status, :green)
      "failed" -> Owl.Data.tag(status, :red)
      "running" -> Owl.Data.tag(status, :yellow)
      _ -> Owl.Data.tag(status, :white)
    end
  end

  defp output_format(opts, default) do
    opts
    |> Keyword.get(:output, Atom.to_string(default))
    |> String.to_atom()
  end

  defp format_time(nil), do: "-"
  defp format_time(value), do: DateTime.to_iso8601(value)

  defp exit_code(:ok), do: 0
  defp exit_code(_), do: 1
end
