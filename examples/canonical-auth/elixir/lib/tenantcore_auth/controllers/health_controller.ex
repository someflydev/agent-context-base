defmodule TenantcoreAuth.HealthController do
  use TenantcoreAuth, :controller

  def index(conn, _params) do
    json(conn, %{status: "ok"})
  end
end
