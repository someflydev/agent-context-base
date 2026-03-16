# Seam example: Elixir coordinator — NATS JetStream publisher + completion subscriber
# Seam 1 of 2: Elixir → Go via NATS JetStream (Elixir publishes work tasks, Go consumes)
# Loop-back: Go → Elixir via NATS JetStream (Go publishes completions, Elixir receives)
# Not a full Phoenix/OTP application. See context/stacks/trio-elixir-go-rust.md.
#
# Architecture: [Elixir Coordinator] ── NATS ──► [Go Workers] ── gRPC ──► [Rust Kernel]
# Elixir owns the coordination layer: it decides when work is dispatched and monitors completion.
# Go owns execution: it subscribes to the task queue and orchestrates the Rust gRPC call.
#
# Dependencies (mix.exs):
#   {:gnat, "~> 1.7"}
#   {:jason, "~> 1.4"}
#   {:plug_cowboy, "~> 2.7"}
#
# Environment:
#   NATS_URL  — NATS server URL (default: nats://localhost:4222)
#   HTTP_PORT — HTTP port for /healthz endpoint (default: 4000)

defmodule ElixirCoordinator.Application do
  use Application

  def start(_type, _args) do
    http_port = System.get_env("HTTP_PORT", "4000") |> String.to_integer()
    children = [
      {ElixirCoordinator.TaskCoordinator, []},
      {Plug.Cowboy, scheme: :http, plug: ElixirCoordinator.Router, options: [port: http_port]}
    ]
    Supervisor.start_link(children, strategy: :one_for_one, name: ElixirCoordinator.Supervisor)
  end
end


# ── Seam interaction: Elixir as the coordination layer ──
# Elixir decides when work is dispatched by publishing to NATS.
# Elixir monitors the coordination loop by subscribing to completions from Go.

defmodule ElixirCoordinator.TaskCoordinator do
  @moduledoc """
  GenServer that:
  1. Publishes a demo task to NATS subject "work.tasks.dispatch" (seam outbound → Go)
  2. Subscribes to "work.tasks.completed" to close the coordination loop (inbound ← Go)

  Go workers subscribe to "work.tasks.dispatch", call the Rust gRPC kernel,
  then publish the result to "work.tasks.completed". Elixir receives that completion,
  closing the coordination loop.

  This is the INVERTED topology from go-elixir-nats: here Elixir is the publisher
  (coordinator) and Go is the subscriber (executor). In go-elixir-nats, Go publishes
  and Elixir subscribes.
  """
  use GenServer
  require Logger

  @stream_name "WORK_TASKS"
  @dispatch_subject "work.tasks.dispatch"
  @completed_subject "work.tasks.completed"

  def start_link(_opts), do: GenServer.start_link(__MODULE__, %{}, name: __MODULE__)

  def init(state) do
    nats_url = System.get_env("NATS_URL", "nats://localhost:4222")
    %URI{host: host, port: port} = URI.parse(nats_url)
    {:ok, conn} = Gnat.start_link(%{host: host, port: port || 4222})

    # Ensure the WORK_TASKS stream exists — covers both subjects (idempotent)
    :ok = ensure_stream(conn)

    # ── Seam loop-back: subscribe to "work.tasks.completed" ──
    # Elixir monitors Go's completions to close the coordination loop.
    # This subscription demonstrates that Elixir sees every result that Go produces.
    {:ok, _sub} = Gnat.sub(conn, self(), @completed_subject)
    Logger.info("elixir-coordinator: subscribed to #{@completed_subject}")

    # ── Seam outbound: publish demo task to "work.tasks.dispatch" ──
    # In production, Elixir's OTP supervision tree drives this based on scheduling
    # logic, retry policy, and per-instrument state. Here one demo task is published
    # on startup to demonstrate the seam flow.
    :ok = publish_task(conn, %{
      task_id:        "task-demo-001",
      correlation_id: "coord-001",
      task_type:      "compute.normalize",
      data:           %{values: [1.0, 3.0, 5.0, 2.0, 4.0], operation: "normalize"}
    })

    {:ok, %{conn: conn}}
  end

  # ── Seam loop-back: receive completion event from Go via NATS ──
  def handle_info({:msg, %{subject: @completed_subject, body: body}}, state) do
    case Jason.decode(body) do
      {:ok, event} ->
        Logger.info(
          "completion received from Go: task_id=#{event["task_id"]} " <>
          "result_summary=#{event["result_summary"]} " <>
          "duration_ns=#{event["duration_ns"]}"
        )
      {:error, reason} ->
        Logger.error("failed to decode completion event: #{inspect(reason)}")
    end
    {:noreply, state}
  end

  def handle_info(_msg, state), do: {:noreply, state}

  # ── Seam outbound: publish task to "work.tasks.dispatch" → Go workers ──
  # Event shape: payload_version, task_id, correlation_id, published_at, task_type, data
  defp publish_task(conn, %{task_id: task_id, correlation_id: correlation_id,
                             task_type: task_type, data: data}) do
    payload = Jason.encode!(%{
      payload_version: 1,
      task_id:         task_id,
      correlation_id:  correlation_id,
      published_at:    DateTime.utc_now() |> DateTime.to_iso8601(),
      task_type:       task_type,
      data:            data
    })
    case Gnat.pub(conn, @dispatch_subject, payload) do
      :ok ->
        Logger.info("task published to NATS: task_id=#{task_id} subject=#{@dispatch_subject}")
        :ok
      {:error, reason} ->
        Logger.error("failed to publish task: #{inspect(reason)}")
        {:error, reason}
    end
  end

  defp ensure_stream(conn) do
    case Gnat.Jetstream.API.Stream.create(conn, %{
      name:     @stream_name,
      subjects: ["work.tasks.>"]
    }) do
      {:ok, _}                           -> :ok
      {:error, %{"err_code" => 10058}}   -> :ok   # stream already exists — safe to continue
      {:error, reason}                   -> raise "failed to ensure NATS stream: #{inspect(reason)}"
    end
  end
end


# ── Health endpoint ──
# Checks NATS connectivity by verifying the coordinator process is alive.

defmodule ElixirCoordinator.Router do
  use Plug.Router

  plug :match
  plug :dispatch

  get "/healthz" do
    # The coordinator GenServer alive implies NATS connected; init/1 raises on NATS failure.
    case Process.whereis(ElixirCoordinator.TaskCoordinator) do
      nil ->
        conn
        |> put_resp_content_type("application/json")
        |> send_resp(503, Jason.encode!(%{status: "degraded", reason: "coordinator not started"}))
      _pid ->
        conn
        |> put_resp_content_type("application/json")
        |> send_resp(200, Jason.encode!(%{status: "ok"}))
    end
  end

  match _ do
    send_resp(conn, 404, "not found")
  end
end
