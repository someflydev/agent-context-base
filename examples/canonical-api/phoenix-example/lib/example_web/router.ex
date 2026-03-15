defmodule ExampleWeb.Router do
  use Phoenix.Router

  pipeline :api do
    plug :accepts, ["json"]
  end

  pipeline :fragment do
    plug :accepts, ["html"]
  end

  scope "/", ExampleWeb do
    pipe_through :api

    get "/healthz", HealthController, :show
    get "/api/reports/:tenant_id", ReportController, :index
    get "/data/chart/:metric", ChartController, :show
  end

  scope "/fragments", ExampleWeb do
    pipe_through :fragment

    get "/report-card/:tenant_id", FragmentController, :show
  end
end
