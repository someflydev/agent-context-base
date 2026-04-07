defmodule Taskflow.CLI.Main do
  alias Taskflow.CLI.Output
  alias Taskflow.Core.{Filter, Loader, Stats}
  alias Taskflow.JobStore

  def main(argv) do
    dispatch(argv)
    |> exit_code()
    |> System.halt()
  end

  def dispatch(argv) do
    {opts, args} = parse_args(argv)
    fixtures_path = Keyword.get(opts, :fixtures_path, Loader.default_fixtures_path())

    case args do
      ["list"] ->
        jobs =
          fixtures_path
          |> Loader.load_jobs()
          |> Filter.filter(status: Keyword.get(opts, :status), tag: Keyword.get(opts, :tag))
          |> Filter.sort(:started_at)

        Output.print_jobs(jobs, output_format(opts, :table))
        :ok

      ["inspect", job_id] ->
        job =
          fixtures_path
          |> Loader.load_jobs()
          |> Enum.find(&(&1.id == job_id))

        if job do
          Output.print_job(job, output_format(opts, :plain))
          :ok
        else
          Output.print_error("job not found: #{job_id}")
          {:error, :not_found}
        end

      ["stats"] ->
        fixtures_path
        |> Loader.load_jobs()
        |> Stats.compute()
        |> Output.print_stats(output_format(opts, :plain))

        :ok

      ["watch"] ->
        if Keyword.get(opts, :no_tui, false) do
          fixtures_path
          |> Loader.load_jobs()
          |> Filter.sort(:started_at)
          |> Output.print_jobs(:table)

          :ok
        else
          with :ok <- JobStore.ensure_started(fixtures_path) do
            Ratatouille.Runtime.start(app: Taskflow.Tui.App)
          end
        end

      _ ->
        parser_banner()
        {:error, :invalid_args}
    end
  rescue
    e in Loader.FixtureError ->
      Output.print_error(e.message)
      {:error, :fixture_error}
  end

  def parser do
    if Code.ensure_loaded?(Optimus) do
      apply(Optimus, :new!, [
        [
          name: "taskflow",
          description: "TaskFlow Monitor",
          version: "0.1.0",
          author: "OpenAI",
          about: "TaskFlow terminal monitor"
        ]
      ])
    else
      nil
    end
  end

  defp parse_args(argv) do
    _ = parser()

    {opts, rest, _invalid} =
      OptionParser.parse(argv,
        strict: [
          status: :string,
          tag: :string,
          output: :string,
          fixtures_path: :string,
          no_tui: :boolean
        ],
        aliases: [f: :fixtures_path]
      )

    {opts, rest}
  end

  defp output_format(opts, default) do
    opts
    |> Keyword.get(:output, Atom.to_string(default))
    |> String.to_atom()
  end

  defp parser_banner do
    IO.puts("taskflow <list|inspect|stats|watch> [options]")
  end

  defp exit_code(:ok), do: 0
  defp exit_code(_), do: 1
end
