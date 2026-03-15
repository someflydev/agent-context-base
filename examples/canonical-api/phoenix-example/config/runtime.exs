import Config

port = String.to_integer(System.get_env("PORT", "4000"))
config :example, ExampleWeb.Endpoint, http: [ip: {0, 0, 0, 0}, port: port]
