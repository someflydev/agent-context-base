defmodule WorkspaceSyncContext.SyncRun do
  use Ecto.Schema
  import Ecto.Changeset

  @moduledoc """
  Lane A example using Ecto.Changeset.
  The changeset/2 function defines the cast-then-validate pipeline.
  Casting converts raw params to typed struct fields.
  Validation checks constraints and cross-field rules.
  These are two distinct phases in the pipeline.
  """

  @statuses ~w[pending running succeeded failed cancelled]
  @triggers ~w[manual scheduled webhook]

  embedded_schema do
    field :run_id, :string
    field :workspace_id, :string
    field :status, :string
    field :trigger, :string
    field :started_at, :utc_datetime_usec
    field :finished_at, :utc_datetime_usec
    field :duration_ms, :integer
    field :records_ingested, :integer
    field :error_code, :string
  end

  def changeset(run, attrs) do
    run
    |> cast(attrs, [:run_id, :workspace_id, :status, :trigger, :started_at, :finished_at, :duration_ms, :records_ingested, :error_code])
    |> validate_required([:run_id, :workspace_id, :status, :trigger])
    |> validate_inclusion(:status, @statuses)
    |> validate_inclusion(:trigger, @triggers)
    |> validate_number(:duration_ms, greater_than_or_equal_to: 0)
    |> validate_number(:records_ingested, greater_than_or_equal_to: 0, less_than_or_equal_to: 10_000_000)
    |> validate_finished_timestamps()
    |> validate_duration_required()
    |> validate_error_code_rule()
  end

  defp validate_finished_timestamps(changeset) do
    started_at = get_field(changeset, :started_at)
    finished_at = get_field(changeset, :finished_at)

    cond do
      finished_at && is_nil(started_at) ->
        add_error(changeset, :started_at, "must be present when finished_at is set")

      finished_at && started_at && DateTime.compare(finished_at, started_at) == :lt ->
        add_error(changeset, :finished_at, "must be after started_at")

      true ->
        changeset
    end
  end

  defp validate_duration_required(changeset) do
    if get_field(changeset, :finished_at) && is_nil(get_field(changeset, :duration_ms)) do
      add_error(changeset, :duration_ms, "is required when finished_at is set")
    else
      changeset
    end
  end

  defp validate_error_code_rule(changeset) do
    status = get_field(changeset, :status)
    error_code = get_field(changeset, :error_code)

    cond do
      status == "failed" && is_nil(error_code) ->
        add_error(changeset, :error_code, "must be present when status is failed")

      status != "failed" && !is_nil(error_code) ->
        add_error(changeset, :error_code, "must be nil unless status is failed")

      true ->
        changeset
    end
  end
end
