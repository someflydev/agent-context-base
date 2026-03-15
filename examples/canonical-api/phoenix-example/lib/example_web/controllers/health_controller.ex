defmodule ExampleWeb.HealthController do
  use ExampleWeb, :controller

  def show(conn, _params) do
    json(conn, %{status: "ok", service: "phoenix-example"})
  end
end
