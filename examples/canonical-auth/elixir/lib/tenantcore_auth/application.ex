defmodule TenantcoreAuth.Application do
  use Application

  @impl true
  def start(_type, _args) do
    children = [
      TenantcoreAuth.Domain.InMemoryStore,
      TenantcoreAuth.Endpoint
    ]

    Supervisor.start_link(children, strategy: :one_for_one, name: TenantcoreAuth.Supervisor)
  end

  @impl true
  def config_change(changed, _new, removed) do
    TenantcoreAuth.Endpoint.config_change(changed, removed)
    :ok
  end
end
