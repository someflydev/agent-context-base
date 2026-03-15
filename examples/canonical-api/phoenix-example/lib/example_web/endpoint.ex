defmodule ExampleWeb.Endpoint do
  use Phoenix.Endpoint, otp_app: :example

  plug Plug.RequestId
  plug Plug.Logger, log: :debug
  plug ExampleWeb.Router
end
