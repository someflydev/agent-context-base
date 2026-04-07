defmodule Taskflow.Tui.App do
  @behaviour Ratatouille.App

  import Ratatouille.View

  alias Taskflow.Core.{Filter, Stats}
  alias Taskflow.JobStore
  alias Taskflow.Tui.Components.{JobDetail, JobList, StatusBar}
  alias Taskflow.Tui.State

  @impl true
  def init(_context) do
    jobs = JobStore.get_jobs()
    %State{jobs: jobs, selected: 0, filter: nil}
  end

  @impl true
  def update(model, msg) do
    case msg do
      {:event, %{ch: ?q}} ->
        Ratatouille.Runtime.Command.quit()

      {:event, %{ch: ?r}} ->
        JobStore.refresh()
        %{model | jobs: JobStore.get_jobs()}

      {:event, %{key: key}} when key in [:"arrow_up", 65, 65517] ->
        %{model | selected: max(model.selected - 1, 0)}

      {:event, %{key: key}} when key in [:"arrow_down", 66, 65516] ->
        %{model | selected: min(model.selected + 1, max(length(model.jobs) - 1, 0))}

      _ ->
        model
    end
  end

  @impl true
  def render(model) do
    selected_job = Enum.at(model.jobs, model.selected)
    stats = Stats.compute(model.jobs)

    view do
      panel title: "TaskFlow Monitor" do
        [
          StatusBar.render(stats),
          row do
            [
              column(size: 6, do: JobList.render(model.jobs, model.selected)),
              column(size: 6, do: JobDetail.render(selected_job))
            ]
          end,
          label(content: "q quit | r refresh")
        ]
      end
    end
  end

  def initial_jobs(fixtures_path) do
    fixtures_path
    |> Taskflow.Core.Loader.load_jobs()
    |> Filter.sort(:started_at)
  end
end
