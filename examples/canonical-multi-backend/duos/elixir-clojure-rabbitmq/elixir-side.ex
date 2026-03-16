# Seam example: Elixir Broadway consumer via RabbitMQ (broadway_rabbitmq)
# This is a seam-focused example — shows only connection setup, queue declaration,
# consume loop, and a health endpoint. For full application scaffolding, see
# context/archetypes/multi-backend-service.md and context/stacks/elixir-phoenix.md
#
# Dependencies (add to mix.exs):
#   {:broadway, "~> 1.0"},
#   {:broadway_rabbitmq, "~> 0.7"},
#   {:amqp, "~> 3.3"},
#   {:jason, "~> 1.4"},
#   {:plug_cowboy, "~> 2.6"}
#
# Environment:
#   RABBITMQ_HOST  (default: "rabbitmq")
#   RABBITMQ_USER  (default: "guest")
#   RABBITMQ_PASS  (default: "guest")
#   HTTP_PORT      (default: "4000")

defmodule ElixirSide.QueueSetup do
  @moduledoc """
  Declares the exchange, queue (with DLX), and binding before Broadway starts.
  Safe to call on every restart — AMQP declarations are idempotent.
  """

  def run do
    host = System.get_env("RABBITMQ_HOST", "rabbitmq")
    user = System.get_env("RABBITMQ_USER", "guest")
    pass = System.get_env("RABBITMQ_PASS", "guest")

    {:ok, conn} = AMQP.Connection.open(host: host, username: user, password: pass)
    {:ok, channel} = AMQP.Channel.open(conn)

    # Declare topic exchange (durable)
    :ok = AMQP.Exchange.topic(channel, "domain-events", durable: true)

    # Declare dead-letter exchange
    :ok = AMQP.Exchange.direct(channel, "domain-events.dlx", durable: true)

    # Declare main queue with DLX arguments
    {:ok, _} =
      AMQP.Queue.declare(channel, "domain.tasks.enriched",
        durable: true,
        arguments: [
          {"x-dead-letter-exchange", :longstr, "domain-events.dlx"},
          {"x-dead-letter-routing-key", :longstr, "domain.tasks.failed"}
        ]
      )

    # Declare dead-letter queue and bind it to the DLX
    {:ok, _} = AMQP.Queue.declare(channel, "domain.tasks.dlq", durable: true)

    :ok =
      AMQP.Queue.bind(channel, "domain.tasks.dlq", "domain-events.dlx",
        routing_key: "domain.tasks.failed"
      )

    # Bind main queue to topic exchange — pattern "domain.tasks.*" matches
    # routing keys like "domain.tasks.created", "domain.tasks.updated", etc.
    :ok =
      AMQP.Queue.bind(channel, "domain.tasks.enriched", "domain-events",
        routing_key: "domain.tasks.*"
      )

    AMQP.Channel.close(channel)
    AMQP.Connection.close(conn)
    :ok
  end
end

defmodule ElixirSide.Consumer do
  use Broadway

  require Logger

  def start_link(_opts) do
    host = System.get_env("RABBITMQ_HOST", "rabbitmq")
    user = System.get_env("RABBITMQ_USER", "guest")
    pass = System.get_env("RABBITMQ_PASS", "guest")

    Broadway.start_link(__MODULE__,
      name: __MODULE__,
      producer: [
        module:
          {BroadwayRabbitMQ.Producer,
           queue: "domain.tasks.enriched",
           connection: [
             host: host,
             port: 5672,
             username: user,
             password: pass
           ],
           # reject_and_requeue_once: on first failure, requeue;
           # on second failure, reject without requeue → routes to DLX
           on_failure: :reject_and_requeue_once,
           qos: [prefetch_count: 10]},
        concurrency: 1
      ],
      processors: [
        default: [concurrency: 4]
      ]
    )
  end

  @impl true
  def handle_message(_processor, message, _context) do
    case Jason.decode(message.data) do
      {:ok, event} ->
        handle_event(message, event)

      {:error, reason} ->
        Logger.error("failed to decode message body: #{inspect(reason)}")
        Broadway.Message.failed(message, "json_decode_error")
    end
  end

  defp handle_event(message, %{"payload_version" => 1} = event) do
    Logger.info(
      "received task " <>
        "event_type=#{event["event_type"]} " <>
        "entity_id=#{event["entity_id"]} " <>
        "tenant_id=#{event["tenant_id"]} " <>
        "correlation_id=#{event["correlation_id"]}"
    )

    message
  end

  defp handle_event(message, %{"payload_version" => v}) do
    Logger.warning("unsupported payload_version=#{v}, rejecting")
    Broadway.Message.failed(message, "unsupported_payload_version:#{v}")
  end

  defp handle_event(message, _event) do
    Logger.warning("message missing payload_version, rejecting")
    Broadway.Message.failed(message, "missing_payload_version")
  end
end

defmodule ElixirSide.HealthPlug do
  use Plug.Router

  plug :match
  plug :dispatch

  get "/healthz" do
    conn
    |> put_resp_content_type("application/json")
    |> send_resp(200, ~s({"status":"ok"}))
  end
end

defmodule ElixirSide.Application do
  use Application

  def start(_type, _args) do
    # Declare exchange, queue (with DLX), and binding before Broadway starts.
    # Declarations are idempotent — safe to call on every restart.
    :ok = ElixirSide.QueueSetup.run()

    port = String.to_integer(System.get_env("HTTP_PORT", "4000"))

    children = [
      {Plug.Cowboy, scheme: :http, plug: ElixirSide.HealthPlug, port: port},
      ElixirSide.Consumer
    ]

    opts = [strategy: :one_for_one, name: ElixirSide.Supervisor]
    Supervisor.start_link(children, opts)
  end
end
