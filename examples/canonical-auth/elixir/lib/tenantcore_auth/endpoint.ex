defmodule TenantcoreAuth.Endpoint do
  use Phoenix.Endpoint, otp_app: :tenantcore_auth

  @session_options [
    store: :cookie,
    key: "_tenantcore_auth_key",
    signing_salt: "tenantcore"
  ]

  plug Plug.RequestId

  plug Plug.Parsers,
    parsers: [:urlencoded, :multipart, :json],
    pass: ["*/*"],
    json_decoder: Phoenix.json_library()

  plug Plug.MethodOverride
  plug Plug.Head
  plug Plug.Session, @session_options
  plug TenantcoreAuth.Router
end
