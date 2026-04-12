defmodule WorkspaceSyncContext.SchemaValidator do
  @moduledoc """
  Lane B: validate data against a JSON Schema document using ex_json_schema.
  This is the contract-first approach: the schema is the source of truth,
  not the application code.
  """

  def load_schema(path) do
    path |> File.read!() |> Jason.decode!() |> ExJsonSchema.Schema.resolve()
  end

  def validate_against_schema(data, schema) do
    case ExJsonSchema.Validator.validate(schema, data) do
      :ok -> {:ok, data}
      {:error, errors} -> {:error, errors}
    end
  end

  def demo do
    schema = load_schema("workspace_config.schema.json")

    valid_data =
      "../../domain/fixtures/valid/workspace_config_basic.json"
      |> File.read!()
      |> Jason.decode!()

    invalid_data =
      "../../domain/fixtures/invalid/workspace_config_bad_slug.json"
      |> File.read!()
      |> Jason.decode!()

    IO.puts("Valid fixture: #{inspect(validate_against_schema(valid_data, schema))}")
    IO.puts("Invalid fixture: #{inspect(validate_against_schema(invalid_data, schema))}")
  end
end
