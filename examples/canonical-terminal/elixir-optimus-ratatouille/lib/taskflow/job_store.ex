defmodule Taskflow.JobStore do
  use GenServer

  alias Taskflow.Core.Loader

  def start_link(opts) do
    fixtures_path = Keyword.fetch!(opts, :fixtures_path)
    GenServer.start_link(__MODULE__, fixtures_path, name: __MODULE__)
  end

  def ensure_started(fixtures_path) do
    case Process.whereis(__MODULE__) do
      nil -> start_link(fixtures_path: fixtures_path)
      _pid -> :ok
    end
  end

  def get_jobs, do: GenServer.call(__MODULE__, :get_jobs)
  def refresh, do: GenServer.cast(__MODULE__, :refresh)

  @impl true
  def init(fixtures_path) do
    {:ok, %{fixtures_path: fixtures_path, jobs: Loader.load_jobs(fixtures_path)}}
  end

  @impl true
  def handle_call(:get_jobs, _from, state), do: {:reply, state.jobs, state}

  @impl true
  def handle_cast(:refresh, state) do
    {:noreply, %{state | jobs: Loader.load_jobs(state.fixtures_path)}}
  end
end
