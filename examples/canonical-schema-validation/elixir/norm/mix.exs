defmodule WorkspaceSyncContextNorm.MixProject do
  use Mix.Project

  def project do
    [
      app: :workspace_sync_context_norm,
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
    [{:norm, "~> 0.13"}]
  end
end
