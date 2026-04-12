defmodule WorkspaceSyncContext.IngestionSource do
  use Ecto.Schema
  import Ecto.Changeset

  @moduledoc """
  Lane A example using Ecto.Changeset.
  The changeset/2 function defines the cast-then-validate pipeline.
  Casting converts raw params to typed struct fields.
  Validation checks constraints and cross-field rules.
  These are two distinct phases in the pipeline.
  """

  @source_types ~w[http_poll webhook_push file_watch database_cdc]

  embedded_schema do
    field :source_id, :string
    field :source_type, :string
    field :config, :map
    field :enabled, :boolean
    field :poll_interval_seconds, :integer
  end

  def changeset(source, attrs) do
    source
    |> cast(attrs, [:source_id, :source_type, :config, :enabled, :poll_interval_seconds])
    |> validate_required([:source_id, :source_type, :config, :enabled])
    |> validate_inclusion(:source_type, @source_types)
    |> validate_config_shape()
    |> validate_poll_interval()
  end

  defp validate_config_shape(changeset) do
    source_type = get_field(changeset, :source_type)
    config = get_field(changeset, :config) || %{}

    required_fields =
      case source_type do
        "http_poll" -> ~w[url method headers]
        "webhook_push" -> ~w[path secret]
        "file_watch" -> ~w[path pattern]
        "database_cdc" -> ~w[dsn table cursor_field]
        _ -> []
      end

    Enum.reduce(required_fields, changeset, fn field, acc ->
      if Map.has_key?(config, field), do: acc, else: add_error(acc, :config, "#{field} is required for #{source_type}")
    end)
  end

  defp validate_poll_interval(changeset) do
    source_type = get_field(changeset, :source_type)
    poll_interval = get_field(changeset, :poll_interval_seconds)

    cond do
      source_type == "http_poll" && (is_nil(poll_interval) || poll_interval < 60) ->
        add_error(changeset, :poll_interval_seconds, "must be present and >= 60 for http_poll")

      source_type != "http_poll" && !is_nil(poll_interval) ->
        add_error(changeset, :poll_interval_seconds, "must be nil unless source_type is http_poll")

      true ->
        changeset
    end
  end
end
