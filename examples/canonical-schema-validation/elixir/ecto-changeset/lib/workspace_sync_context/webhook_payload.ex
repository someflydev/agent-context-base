defmodule WorkspaceSyncContext.WebhookPayload do
  use Ecto.Schema
  import Ecto.Changeset

  @moduledoc """
  Lane A example using Ecto.Changeset.
  The changeset/2 function defines the cast-then-validate pipeline.
  Casting converts raw params to typed struct fields.
  Validation checks constraints and cross-field rules.
  These are two distinct phases in the pipeline.
  """

  @event_types ~w[sync.completed sync.failed workspace.suspended]
  @reasons ~w[policy_violation payment_failure manual]

  embedded_schema do
    field :event_type, :string
    field :payload_version, :string
    field :timestamp, :utc_datetime_usec
    field :signature, :string
    field :data, :map
  end

  def changeset(payload, attrs) do
    payload
    |> cast(attrs, [:event_type, :payload_version, :timestamp, :signature, :data])
    |> validate_required([:event_type, :payload_version, :timestamp, :signature, :data])
    |> validate_inclusion(:event_type, @event_types)
    |> validate_inclusion(:payload_version, ~w[v1 v2 v3])
    |> validate_format(:signature, ~r/^[a-f0-9]{64}$/)
    |> validate_union_data()
  end

  defp validate_union_data(changeset) do
    event_type = get_field(changeset, :event_type)
    data = get_field(changeset, :data) || %{}

    required_fields =
      case event_type do
        "sync.completed" -> ~w[run_id workspace_id duration_ms records_ingested]
        "sync.failed" -> ~w[run_id workspace_id error_code error_message]
        "workspace.suspended" -> ~w[workspace_id suspended_until reason]
        _ -> []
      end

    changeset =
      Enum.reduce(required_fields, changeset, fn field, acc ->
        if Map.has_key?(data, field), do: acc, else: add_error(acc, :data, "#{field} is required for #{event_type}")
      end)

    if event_type == "workspace.suspended" && Map.get(data, "reason") not in @reasons do
      add_error(changeset, :data, "reason must be one of #{Enum.join(@reasons, ", ")}")
    else
      changeset
    end
  end
end
