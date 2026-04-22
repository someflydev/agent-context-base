defmodule TenantcoreAuth.MixProject do
  use Mix.Project

  def project do
    [
      app: :tenantcore_auth,
      version: "0.1.0",
      elixir: "~> 1.16",
      elixirc_paths: elixirc_paths(Mix.env()),
      start_permanent: Mix.env() == :prod,
      deps: deps()
    ]
  end

  def application do
    [
      mod: {TenantcoreAuth.Application, []},
      extra_applications: [:logger, :runtime_tools]
    ]
  end

  defp elixirc_paths(:test), do: ["lib", "test/support", "test/tenantcore_auth/support"]
  defp elixirc_paths(_), do: ["lib"]

  defp deps do
    [
      {:phoenix, "~> 1.7"},
      {:jason, "~> 1.4"},
      {:joken, "~> 2.6"},
      {:jose, "~> 1.11"},
      {:plug_cowboy, "~> 2.7"}
    ]
  end
end
