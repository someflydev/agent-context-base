defmodule WorkspaceSyncContext.ReviewRequest do
  use Ecto.Schema
  import Ecto.Changeset

  @moduledoc """
  Lane A example using Ecto.Changeset.
  The changeset/2 function defines the cast-then-validate pipeline.
  Casting converts raw params to typed struct fields.
  Validation checks constraints and cross-field rules.
  These are two distinct phases in the pipeline.
  """

  @priorities ~w[low normal high critical]

  embedded_schema do
    field :request_id, :string
    field :workspace_id, :string
    field :reviewer_emails, {:array, :string}, default: []
    field :content_ids, {:array, :string}, default: []
    field :priority, :string
    field :due_at, :utc_datetime_usec
    field :notes, :string
  end

  def changeset(request, attrs) do
    request
    |> cast(attrs, [:request_id, :workspace_id, :reviewer_emails, :content_ids, :priority, :due_at, :notes])
    |> validate_required([:request_id, :workspace_id, :reviewer_emails, :content_ids, :priority])
    |> validate_inclusion(:priority, @priorities)
    |> validate_length(:reviewer_emails, min: 1, max: 5)
    |> validate_length(:content_ids, min: 1, max: 50)
    |> validate_reviewer_emails()
    |> validate_unique_lists()
    |> validate_change(:notes, fn :notes, value ->
      if is_nil(value) or String.length(value) <= 2000, do: [], else: [notes: "must be <= 2000 chars"]
    end)
    |> validate_due_at_rule()
  end

  defp validate_reviewer_emails(changeset) do
    emails = get_field(changeset, :reviewer_emails) || []

    if Enum.all?(emails, &String.match?(&1, ~r/.+@.+\..+/)) do
      changeset
    else
      add_error(changeset, :reviewer_emails, "must contain valid email addresses")
    end
  end

  defp validate_unique_lists(changeset) do
    changeset
    |> maybe_add_duplicate_error(:reviewer_emails)
    |> maybe_add_duplicate_error(:content_ids)
  end

  defp maybe_add_duplicate_error(changeset, field) do
    values = get_field(changeset, field) || []
    if Enum.uniq(values) == values, do: changeset, else: add_error(changeset, field, "must be unique")
  end

  defp validate_due_at_rule(changeset) do
    if get_field(changeset, :priority) == "critical" && is_nil(get_field(changeset, :due_at)) do
      add_error(changeset, :due_at, "is required when priority is critical")
    else
      changeset
    end
  end
end
