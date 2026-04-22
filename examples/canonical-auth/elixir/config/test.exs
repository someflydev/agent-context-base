import Config

config :tenantcore_auth, TenantcoreAuth.Endpoint,
  http: [ip: {127, 0, 0, 1}, port: 4002],
  server: false

config :logger, level: :warning
