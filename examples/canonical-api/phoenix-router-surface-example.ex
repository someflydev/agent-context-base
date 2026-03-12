defmodule ExampleWeb.Router do
  use ExampleWeb, :router

  pipeline :browser do
    plug :accepts, ["html"]
    plug :fetch_session
    plug :put_root_layout, html: {ExampleWeb.Layouts, :root}
    plug :protect_from_forgery
    plug :put_secure_browser_headers
  end

  scope "/", ExampleWeb do
    pipe_through :browser

    get "/tenants/:tenant_id/reports", ReportController, :index
  end
end

