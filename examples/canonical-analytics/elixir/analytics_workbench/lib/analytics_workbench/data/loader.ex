defmodule AnalyticsWorkbench.Data.Loader do
  @doc """
  Loads fixture data from the canonical-analytics domain fixtures directory.
  Dogfoods examples/canonical-faker/ via the shared fixture files produced
  by examples/canonical-analytics/domain/generate_fixtures.py.
  """

  def load_fixtures(profile \\ :smoke) do
    path = fixture_path(profile)
    path |> File.read!() |> Jason.decode!(keys: :atoms)
  end

  def fixture_path(profile) do
    base = System.get_env("FIXTURE_PATH") ||
      Path.join([__DIR__, "../../../../../domain/fixtures"])
    Path.join(base, "#{profile}.json")
  end
end
