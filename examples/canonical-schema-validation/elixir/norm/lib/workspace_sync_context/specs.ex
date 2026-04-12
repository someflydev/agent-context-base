defmodule WorkspaceSyncContext.Specs do
  import Norm

  def workspace_config_spec do
    schema(%{
      id: spec(is_binary()),
      name: spec(is_binary() and &(String.length(&1) >= 3) and &(String.length(&1) <= 100)),
      slug: spec(is_binary() and &Regex.match?(~r/^[a-z][a-z0-9-]{1,48}[a-z0-9]$/, &1)),
      owner_email: spec(is_binary() and &String.contains?(&1, "@")),
      plan: one_of(["free", "pro", "enterprise"]),
      max_sync_runs: spec(is_integer() and &(&1 >= 1) and &(&1 <= 1000)),
      settings: settings_block_spec(),
      tags: coll_of(spec(is_binary()), min_count: 0, max_count: 20),
      created_at: spec(is_binary()),
      suspended_until: spec(is_nil() or is_binary())
    })
    |> spec(fn config ->
      limit =
        case config.plan do
          "free" -> 10
          "pro" -> 100
          _ -> 1000
        end

      config.max_sync_runs <= limit
    end)
  end

  def sync_run_spec do
    schema(%{
      run_id: spec(is_binary()),
      workspace_id: spec(is_binary()),
      status: one_of(["pending", "running", "succeeded", "failed", "cancelled"]),
      trigger: one_of(["manual", "scheduled", "webhook"]),
      started_at: spec(is_nil() or is_binary()),
      finished_at: spec(is_nil() or is_binary()),
      duration_ms: spec(is_nil() or (is_integer() and &(&1 >= 0))),
      records_ingested: spec(is_nil() or (is_integer() and &(&1 >= 0) and &(&1 <= 10_000_000))),
      error_code: spec(is_nil() or is_binary())
    })
    |> spec(fn run ->
      cond do
        run.finished_at && is_nil(run.started_at) -> false
        run.finished_at && is_nil(run.duration_ms) -> false
        run.status == "failed" && is_nil(run.error_code) -> false
        run.status != "failed" && !is_nil(run.error_code) -> false
        true -> true
      end
    end)
  end

  def settings_block_spec do
    schema(%{
      retry_max: spec(is_integer() and &(&1 >= 0) and &(&1 <= 10)),
      timeout_seconds: spec(is_integer() and &(&1 >= 10) and &(&1 <= 3600)),
      notify_on_failure: spec(is_boolean()),
      webhook_url: spec(is_nil() or is_binary())
    })
  end
end
