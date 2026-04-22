import Config

config :tenantcore_auth, TenantcoreAuth.Endpoint,
  url: [host: "localhost"],
  adapter: Phoenix.Endpoint.Cowboy2Adapter,
  render_errors: [formats: [json: TenantcoreAuth.ErrorJSON], layout: false],
  pubsub_server: TenantcoreAuth.PubSub,
  secret_key_base: "tenantcore-auth-dev-secret-key-base"

config :phoenix, :json_library, Jason

import_config "#{config_env()}.exs"
