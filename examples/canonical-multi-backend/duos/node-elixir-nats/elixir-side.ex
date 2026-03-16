# This is a seam-focused example.
# For a full application scaffold, see context/archetypes/multi-backend-service.md.
#
# elixir-side.ex — Elixir service: bidirectional NATS seam via Gnat.
#
# Elixir owns distributed state. This side:
#   1. Connects to NATS (core NATS — no JetStream).
#   2. Subscribes to "actions.>" to receive all client actions from Node.
#   3. On each action: decodes the JSON payload and publishes a state update
#      back to "state.{doc_id}.updates" for Node to relay to clients.
#   4. Exposes GET /healthz via a minimal Phoenix router.
#
# This is BIDIRECTIONAL: Elixir both subscribes (client actions from Node) and
# publishes (state updates back to Node). Contrast with go-elixir-nats where
# Elixir only subscribes (unidirectional).
#
# Dependencies (mix.exs):
#   {:gnat, "~> 1.7"}
#   {:jason, "~> 1.4"}
#   {:phoenix, "~> 1.7"}
#
# Environment variables:
#   NATS_URL   NATS server URL (default: nats://nats:4222)
#   PORT       HTTP listen port (default: 4000)

defmodule SeamExample.Application do
  use Application

  def start(_type, _args) do
    children = [
      SeamExample.NatsSeam,
      SeamExample.Web.Endpoint,
    ]
    opts = [strategy: :one_for_one, name: SeamExample.Supervisor]
    Supervisor.start_link(children, opts)
  end
end

defmodule SeamExample.NatsSeam do
  @moduledoc """
  GenServer that holds the NATS connection, subscribes to "actions.>" (all client
  actions from Node), processes each action, and publishes state updates back to
  "state.{doc_id}.updates" for Node to relay to connected clients.

  This is the bidirectional NATS seam — Elixir both subscribes and publishes.
  """
  use GenServer
  require Logger

  def start_link(opts \\ []) do
    GenServer.start_link(__MODULE__, opts, name: __MODULE__)
  end

  # --- GenServer callbacks ---

  @impl true
  def init(_opts) do
    {:ok, %{conn: nil}, {:continue, :connect}}
  end

  @impl true
  def handle_continue(:connect, state) do
    nats_url = System.get_env("NATS_URL", "nats://nats:4222")
    {host, port} = parse_nats_url(nats_url)

    case Gnat.start_link(%{host: host, port: port}) do
      {:ok, conn} ->
        Logger.info("NATS connected to #{nats_url}")
        # Subscribe to all client actions from Node.
        # Subject "actions.>" matches: actions.sess-abc.cursor.moved, actions.sess-xyz.key.pressed, etc.
        {:ok, _sub} = Gnat.sub(conn, self(), "actions.>")
        Logger.info("Subscribed to actions.>")
        {:noreply, %{state | conn: conn}}

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

  # Gnat delivers core NATS messages as {:msg, %{topic: t, body: b, reply_to: r}}
  @impl true
  def handle_info({:msg, %{body: body, topic: topic}}, %{conn: conn} = state) do
    case Jason.decode(body) do
      {:ok, action} ->
        handle_action(conn, topic, action)

      {:error, reason} ->
        Logger.warning("failed to decode action on #{topic}: #{inspect(reason)}")
    end

    {:noreply, state}
  end

  @impl true
  def handle_info(_msg, state), do: {:noreply, state}

  # --- Internal ---

  defp handle_action(conn, topic, %{"payload_version" => 1} = action) do
    session_id = action["session_id"]
    action_type = action["action_type"]
    doc_id = get_in(action, ["data", "doc_id"]) || "unknown"

    Logger.info(
      "received action type=#{action_type} session_id=#{session_id} " <>
      "doc_id=#{doc_id} topic=#{topic}"
    )

    # Build and publish state update back to Node.
    # Subject: "state.{doc_id}.updates" — Node subscribes to "state.*.updates".
    state_subject = "state.#{doc_id}.updates"
    state_payload = %{
      payload_version: 1,
      doc_id: doc_id,
      published_at: DateTime.utc_now() |> DateTime.to_iso8601(),
      event_type: "presence.updated",
      data: %{
        cursors: [
          %{
            session_id: session_id,
            x: get_in(action, ["data", "x"]) || 0,
            y: get_in(action, ["data", "y"]) || 0
          }
        ]
      }
    }

    case Jason.encode(state_payload) do
      {:ok, encoded} ->
        :ok = Gnat.pub(conn, state_subject, encoded)
        Logger.info("published state update to #{state_subject} event_type=presence.updated")

      {:error, reason} ->
        Logger.error("failed to encode state payload: #{inspect(reason)}")
    end
  end

  defp handle_action(_conn, topic, %{"payload_version" => v}) do
    Logger.warning("unknown payload_version #{v} on topic #{topic}; dropping")
  end

  defp handle_action(_conn, topic, _action) do
    Logger.warning("action missing payload_version on topic #{topic}; dropping")
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
    seam_alive = Process.whereis(SeamExample.NatsSeam) != nil

    if seam_alive do
      json(conn, %{status: "ok"})
    else
      conn
      |> put_status(:service_unavailable)
      |> json(%{status: "degraded", reason: "nats seam not running"})
    end
  end
end
