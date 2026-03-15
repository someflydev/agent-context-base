import Config

config :example, ExampleWeb.Endpoint,
  adapter: Bandit.PhoenixAdapter,
  http: [ip: {0, 0, 0, 0}, port: 4000],
  server: true

config :phoenix, :json_library, Jason
