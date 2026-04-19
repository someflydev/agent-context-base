defmodule AnalyticsWorkbench.Data.Store do
  use Agent

  def start_link(_) do
    Agent.start_link(fn -> AnalyticsWorkbench.Data.Loader.load_fixtures(:smoke) end,
      name: __MODULE__)
  end

  def get, do: Agent.get(__MODULE__, & &1)
end
