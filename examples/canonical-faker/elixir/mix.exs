defmodule CanonicalFakerElixir.MixProject do
  use Mix.Project
  def project, do: [
    app: :canonical_faker_elixir,
    version: "0.1.0",
    elixir: "~> 1.15",
    deps: deps()
  ]
  defp deps do
    [
      {:faker, "~> 0.18"},
      {:ex_machina, "~> 2.7"},
      {:jason, "~> 1.4"}
    ]
  end
end
