import Config

config :tenantcore_auth, TenantcoreAuth.Endpoint,
  http: [ip: {127, 0, 0, 1}, port: 4000],
  server: true,
  debug_errors: true,
  code_reloader: false,
  check_origin: false,
  secret_key_base: "tenantcore-auth-dev-secret-key-base"

config :logger, :default_formatter,
  format: "$time $metadata[$level] $message\n",
  metadata: [:request_id]
