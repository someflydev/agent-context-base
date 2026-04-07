defmodule TaskflowOwl.MixProject do
  use Mix.Project

  def project do
    [
      app: :taskflow_owl,
      version: "0.1.0",
      elixir: "~> 1.16",
      start_permanent: Mix.env() == :prod,
      deps: deps(),
      escript: [main_module: Taskflow.CLI]
    ]
  end

  def application do
    [
      extra_applications: [:logger]
    ]
  end

  defp deps do
    [
      {:owl, "~> 0.11"},
      {:jason, "~> 1.4"}
    ]
  end
end
