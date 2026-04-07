defmodule Taskflow.MixProject do
  use Mix.Project

  def project do
    [
      app: :taskflow,
      version: "0.1.0",
      elixir: "~> 1.16",
      start_permanent: Mix.env() == :prod,
      deps: deps(),
      escript: [main_module: Taskflow.CLI.Main]
    ]
  end

  def application do
    [
      extra_applications: [:logger],
      mod: {Taskflow.Application, []}
    ]
  end

  defp deps do
    [
      {:optimus, "~> 0.3"},
      {:ratatouille, "~> 0.5"},
      {:jason, "~> 1.4"},
      {:ex_termbox, "~> 1.0"}
    ]
  end
end
