defmodule WorkspaceSyncContext.SettingsBlock do
  use Ecto.Schema
  import Ecto.Changeset

  @moduledoc """
  Lane A example using Ecto.Changeset.
  The changeset/2 function defines the cast-then-validate pipeline.
  Casting converts raw params to typed struct fields.
  Validation checks constraints and cross-field rules.
  These are two distinct phases in the pipeline.
  """

  embedded_schema do
    field :retry_max, :integer
    field :timeout_seconds, :integer
    field :notify_on_failure, :boolean
    field :webhook_url, :string
  end

  def changeset(settings, attrs) do
    settings
    |> cast(attrs, [:retry_max, :timeout_seconds, :notify_on_failure, :webhook_url])
    |> validate_required([:retry_max, :timeout_seconds, :notify_on_failure])
    |> validate_number(:retry_max, greater_than_or_equal_to: 0, less_than_or_equal_to: 10)
    |> validate_number(:timeout_seconds, greater_than_or_equal_to: 10, less_than_or_equal_to: 3600)
    |> validate_change(:webhook_url, fn :webhook_url, value ->
      if is_nil(value) or String.match?(value, ~r/^https?:\/\//), do: [], else: [webhook_url: "must be a valid http/https URL"]
    end)
  end
end

defmodule WorkspaceSyncContext.WorkspaceConfig do
  use Ecto.Schema
  import Ecto.Changeset

  @moduledoc """
  Lane A example using Ecto.Changeset.
  The changeset/2 function defines the cast-then-validate pipeline.
  Casting converts raw params to typed struct fields.
  Validation checks constraints and cross-field rules.
  These are two distinct phases in the pipeline.
  """

  @valid_plans ~w[free pro enterprise]

  embedded_schema do
    field :id, :string
    field :name, :string
    field :slug, :string
    field :owner_email, :string
    field :plan, :string
    field :max_sync_runs, :integer
    field :tags, {:array, :string}, default: []
    field :created_at, :utc_datetime_usec
    field :suspended_until, :utc_datetime_usec
    embeds_one :settings, WorkspaceSyncContext.SettingsBlock
  end

  def changeset(config, attrs) do
    config
    |> cast(attrs, [:id, :name, :slug, :owner_email, :plan, :max_sync_runs, :tags, :created_at, :suspended_until])
    |> cast_embed(:settings, required: true)
    |> validate_required([:id, :name, :slug, :owner_email, :plan, :max_sync_runs, :created_at])
    |> validate_length(:name, min: 3, max: 100)
    |> validate_format(:slug, ~r/^[a-z][a-z0-9-]{1,48}[a-z0-9]$/)
    |> validate_format(:owner_email, ~r/.+@.+\..+/)
    |> validate_inclusion(:plan, @valid_plans)
    |> validate_number(:max_sync_runs, greater_than_or_equal_to: 1, less_than_or_equal_to: 1000)
    |> validate_length(:tags, max: 20)
    |> validate_tag_lengths()
    |> validate_plan_run_limit()
  end

  defp validate_tag_lengths(changeset) do
    tags = get_field(changeset, :tags) || []

    if Enum.all?(tags, &(String.length(&1) in 1..50)) do
      changeset
    else
      add_error(changeset, :tags, "each tag must be 1..50 chars")
    end
  end

  defp validate_plan_run_limit(changeset) do
    plan = get_field(changeset, :plan)
    max_runs = get_field(changeset, :max_sync_runs)

    limit =
      case plan do
        "free" -> 10
        "pro" -> 100
        "enterprise" -> 1000
        _ -> 1000
      end

    if max_runs && max_runs > limit do
      add_error(changeset, :max_sync_runs, "must be <= #{limit} for #{plan} plan")
    else
      changeset
    end
  end
end
