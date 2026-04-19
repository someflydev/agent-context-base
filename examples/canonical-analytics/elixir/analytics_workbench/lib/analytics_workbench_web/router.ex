defmodule AnalyticsWorkbenchWeb.Router do
  use AnalyticsWorkbenchWeb, :router

  pipeline :browser do
    plug :accepts, ["html"]
    plug :fetch_session
    plug :put_root_layout, html: {AnalyticsWorkbenchWeb.Layouts, :root}
    plug :protect_from_forgery
    plug :put_secure_browser_headers
  end

  pipeline :api do
    plug :accepts, ["json"]
  end

  scope "/", AnalyticsWorkbenchWeb do
    pipe_through :browser

    get "/", PageController, :index
    get "/trends", PageController, :trends
    get "/services", PageController, :services
    get "/distributions", PageController, :distributions
    get "/heatmap", PageController, :heatmap
    get "/funnel", PageController, :funnel
    get "/incidents", PageController, :incidents
    
    get "/fragments/chart", FragmentController, :chart
    get "/fragments/summary", FragmentController, :summary
    get "/fragments/details", FragmentController, :details
  end

  scope "/api", AnalyticsWorkbenchWeb do
    pipe_through :api
    get "/health", HealthController, :index
  end
end
