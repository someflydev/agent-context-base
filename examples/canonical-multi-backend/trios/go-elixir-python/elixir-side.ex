# Seam example: Elixir coordinator — NATS subscriber + Python REST caller
# This file shows only the seam layer: two interactions are shown clearly:
#   (1) NATS subscription — consuming jobs.submitted from Go (inbound from Go)
#   (2) HTTP POST to Python /score — calling the inference service (outbound to Python)
# Not a full Phoenix/OTP application. See context/stacks/trio-go-elixir-python.md.

defmodule ElixirCoordinator.Application do
  use Application

  def start(_type, _args) do
    children = [
      {ElixirCoordinator.JobConsumer, []},
      {Plug.Cowboy, scheme: :http, plug: ElixirCoordinator.Router, options: [port: 4000]}
    ]
    opts = [strategy: :one_for_one, name: ElixirCoordinator.Supervisor]
    Supervisor.start_link(children, opts)
  end
end


# ── Seam interaction (1): Consuming jobs.submitted from NATS (inbound from Go) ──

defmodule ElixirCoordinator.JobConsumer do
  @moduledoc """
  GenServer that subscribes to the JOBS stream on NATS and processes
  each submitted job by calling the Python scoring service.
  """
  use GenServer
  require Logger

  @stream_name "JOBS"
  @subject "jobs.submitted"
  @consumer_name "elixir-coordinator"

  def start_link(_opts) do
    GenServer.start_link(__MODULE__, %{}, name: __MODULE__)
  end

  def init(state) do
    nats_url = System.get_env("NATS_URL", "nats://localhost:4222")
    %URI{host: host, port: port} = URI.parse(nats_url)

    {:ok, conn} = Gnat.start_link(%{host: host, port: port || 4222})

    # Ensure the JOBS stream exists (idempotent)
    :ok = ensure_stream(conn)

    # Subscribe to the subject (push consumer for simplicity in this example)
    {:ok, _sub} = Gnat.sub(conn, self(), @subject)

    Logger.info("elixir-coordinator: subscribed to #{@subject}")
    {:ok, Map.merge(state, %{conn: conn})}
  end

  # ── Seam interaction (1): receiving a NATS message from Go ──
  def handle_info({:msg, %{subject: subject, body: body}}, state) do
    case Jason.decode(body) do
      {:ok, event} ->
        Logger.info("received job_id=#{event["job_id"]} from #{subject} correlation_id=#{event["correlation_id"]}")
        process_job(event, state.conn)
      {:error, reason} ->
        Logger.error("failed to decode NATS message: #{inspect(reason)}")
    end
    {:noreply, state}
  end

  def handle_info(_msg, state), do: {:noreply, state}

  # ── Seam interaction (2): calling Python /score (outbound to Python) ──
  defp process_job(event, conn) do
    python_url = System.get_env("PYTHON_SCORE_URL", "http://localhost:8002")

    request_body = Jason.encode!(%{
      job_id: event["job_id"],
      features: event["features"]
    })

    case :httpc.request(
      :post,
      {String.to_charlist(python_url <> "/score"), [], 'application/json', request_body},
      [],
      []
    ) do
      {:ok, {{_, 200, _}, _headers, response_body}} ->
        case Jason.decode(response_body) do
          {:ok, score_result} ->
            Logger.info("scored job_id=#{score_result["job_id"]} score=#{score_result["score"]} label=#{score_result["label"]}")
            # Publish result to jobs.scored so downstream consumers (e.g. Phoenix Channels) can fan out
            publish_scored_result(conn, event["correlation_id"], score_result)
          {:error, reason} ->
            Logger.error("failed to decode Python response: #{inspect(reason)}")
        end
      {:ok, {{_, status, _}, _, _}} ->
        Logger.error("Python scoring returned HTTP #{status} for job_id=#{event["job_id"]}")
      {:error, reason} ->
        Logger.error("failed to call Python scoring for job_id=#{event["job_id"]}: #{inspect(reason)}")
    end
  end

  defp publish_scored_result(conn, correlation_id, score_result) do
    payload = Jason.encode!(%{
      payload_version: 1,
      correlation_id: correlation_id,
      job_id: score_result["job_id"],
      score: score_result["score"],
      label: score_result["label"],
      scored_at: DateTime.utc_now() |> DateTime.to_iso8601()
    })
    case Gnat.pub(conn, "jobs.scored", payload) do
      :ok ->
        Logger.info("published jobs.scored for job_id=#{score_result["job_id"]}")
      {:error, reason} ->
        Logger.error("failed to publish jobs.scored: #{inspect(reason)}")
    end
  end

  defp ensure_stream(conn) do
    case Gnat.Jetstream.API.Stream.create(conn, %{
      name: @stream_name,
      subjects: ["jobs.>"]
    }) do
      {:ok, _} -> :ok
      {:error, %{"err_code" => 10058}} -> :ok  # stream name already in use
      {:error, reason} -> {:error, reason}
    end
  end
end


# ── Health endpoint ──

defmodule ElixirCoordinator.Router do
  use Plug.Router

  plug :match
  plug :dispatch

  get "/healthz" do
    send_resp(conn, 200, Jason.encode!(%{status: "ok"}))
  end

  match _ do
    send_resp(conn, 404, "not found")
  end
end
