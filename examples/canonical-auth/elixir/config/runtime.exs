import Config

if System.get_env("PHX_SERVER") do
  config :tenantcore_auth, TenantcoreAuth.Endpoint, server: true
end

config :tenantcore_auth, TenantcoreAuth.Endpoint,
  http: [port: String.to_integer(System.get_env("PORT", "4000"))]
