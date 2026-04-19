defmodule AnalyticsWorkbench.Filters do
  defstruct date_from: nil, date_to: nil,
            services: [], severity: [], environment: []

  def parse(params) do
    %__MODULE__{
      date_from: Map.get(params, "date_from"),
      date_to: Map.get(params, "date_to"),
      services: parse_multi(params, "services"),
      severity: parse_multi(params, "severity"),
      environment: parse_multi(params, "environment"),
    }
  end

  defp parse_multi(params, key) do
    case Map.get(params, key) do
      nil -> []
      val when is_list(val) -> val
      val when is_binary(val) ->
        if String.contains?(val, ",") do
           String.split(val, ",") |> Enum.reject(&(&1 == ""))
        else
           [val] |> Enum.reject(&(&1 == ""))
        end
    end
  end
end
