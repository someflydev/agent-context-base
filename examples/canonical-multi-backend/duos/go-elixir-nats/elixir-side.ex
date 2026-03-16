# This is a seam-focused example.
# For a full application scaffold, see context/archetypes/multi-backend-service.md.
#
# elixir-side.ex — Elixir service: connects to NATS via Gnat, subscribes to
# domain events with a durable consumer, decodes the JSON payload, and logs
# each received event. Exposes /healthz via a minimal Phoenix router.
#
# Dependencies (mix.exs):
#   {:gnat, "~> 1.7"}
#   {:jason, "~> 1.4"}
#   {:phoenix, "~> 1.7"}

defmodule SeamExample.Application do
  use Application

  def start(_type, _args) do
    children = [
      SeamExample.NatsConsumer,
      SeamExample.Web.Endpoint,
    ]
    opts = [strategy: :one_for_one, name: SeamExample.Supervisor]
    Supervisor.start_link(children, opts)
  end
end

defmodule SeamExample.NatsConsumer do
  @moduledoc """
  GenServer that holds the NATS connection and a durable consumer subscription
  to the "events.>" subject. Reconnects automatically on connection loss.
  """
  use GenServer
  require Logger

  @stream_name "DOMAIN_EVENTS"
  @stream_subjects ["events.>"]
  @consumer_name "elixir-consumer"

  def start_link(opts \\ []) do
    GenServer.start_link(__MODULE__, opts, name: __MODULE__)
  end

  # --- GenServer callbacks ---

  @impl true
  def init(_opts) do
    {:ok, %{conn: nil, subscription: nil}, {:continue, :connect}}
  end

  @impl true
  def handle_continue(:connect, state) do
    nats_url = System.get_env("NATS_URL", "nats://nats:4222")
    {host, port} = parse_nats_url(nats_url)

    case Gnat.start_link(%{host: host, port: port}) do
      {:ok, conn} ->
        Logger.info("NATS connected to #{nats_url}")
        :ok = ensure_stream(conn)
        {:ok, sub} = subscribe(conn)
        {:noreply, %{state | conn: conn, subscription: sub}}

      {:error, reason} ->
        Logger.error("NATS connect failed: #{inspect(reason)}; retrying in 2s")
        Process.send_after(self(), :reconnect, 2_000)
        {:noreply, state}
    end
  end

  @impl true
  def handle_info(:reconnect, state) do
    {:noreply, state, {:continue, :connect}}
  end

  # Gnat delivers messages as {:msg, %{topic: t, body: b, reply_to: r}}
  @impl true
  def handle_info({:msg, %{body: body, topic: topic}}, state) do
    case Jason.decode(body) do
      {:ok, event} ->
        handle_event(topic, event)

      {:error, reason} ->
        Logger.warning("failed to decode message on #{topic}: #{inspect(reason)}")
    end

    {:noreply, state}
  end

  @impl true
  def handle_info(_msg, state), do: {:noreply, state}

  # --- Internal ---

  defp handle_event(topic, %{"payload_version" => 1} = event) do
    Logger.info("received event type=#{event["event_type"]} user_id=#{event["user_id"]} topic=#{topic} correlation_id=#{event["correlation_id"]}")
  end

  defp handle_event(_topic, %{"payload_version" => v}) do
    Logger.warning("unknown payload_version #{v}; dropping message")
  end

  defp handle_event(topic, _event) do
    Logger.warning("event missing payload_version on topic #{topic}; dropping")
  end

  # Ensures the DOMAIN_EVENTS stream exists on NATS.
  # Uses Gnat.Jetstream API — idempotent on repeat calls.
  defp ensure_stream(conn) do
    case Gnat.Jetstream.API.Stream.create(conn, %{
           name: @stream_name,
           subjects: @stream_subjects
         }) do
      {:ok, _} ->
        Logger.info("stream #{@stream_name} ensured")
        :ok

      {:error, %{"description" => "stream name already in use"}} ->
        Logger.debug("stream #{@stream_name} already exists")
        :ok

      {:error, reason} ->
        Logger.error("stream create failed: #{inspect(reason)}")
        :error
    end
  end

  # Creates a push consumer and subscribes to its inbox.
  defp subscribe(conn) do
    inbox = "_INBOX.#{:erlang.unique_integer([:positive])}"

    case Gnat.Jetstream.API.Consumer.create(conn, @stream_name, %{
           durable_name: @consumer_name,
           deliver_subject: inbox,
           ack_policy: :explicit,
           filter_subject: "events.>"
         }) do
      {:ok, _consumer} ->
        Gnat.sub(conn, self(), inbox)

      # Consumer already exists with the same config — reuse it.
      {:error, %{"description" => "consumer name already in use"}} ->
        Gnat.sub(conn, self(), inbox)

      {:error, reason} ->
        {:error, reason}
    end
  end

  defp parse_nats_url("nats://" <> rest) do
    [host, port_str] = String.split(rest, ":")
    {host, String.to_integer(port_str)}
  end

  defp parse_nats_url(url) do
    Logger.warning("unexpected NATS_URL format: #{url}; using defaults")
    {"nats", 4222}
  end
end

defmodule SeamExample.Web.Router do
  use Phoenix.Router

  pipeline :api do
    plug :accepts, ["json"]
  end

  scope "/", SeamExample.Web do
    pipe_through :api
    get "/healthz", HealthController, :index
  end
end

defmodule SeamExample.Web.HealthController do
  use Phoenix.Controller

  def index(conn, _params) do
    consumer_alive = Process.whereis(SeamExample.NatsConsumer) != nil

    if consumer_alive do
      json(conn, %{status: "ok"})
    else
      conn
      |> put_status(:service_unavailable)
      |> json(%{status: "degraded", reason: "nats consumer not running"})
    end
  end
end
