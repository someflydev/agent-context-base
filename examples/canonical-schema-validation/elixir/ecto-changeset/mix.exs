defmodule WorkspaceSyncContext.MixProject do
  use Mix.Project

  def project do
    [
      app: :workspace_sync_context_ecto_changeset,
      version: "0.1.0",
      elixir: "~> 1.16",
      start_permanent: Mix.env() == :prod,
      deps: deps()
    ]
  end

  def application do
    [extra_applications: [:logger]]
  end

  defp deps do
    [{:ecto, "~> 3.12"}]
  end
end
