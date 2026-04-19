defmodule AnalyticsWorkbenchWeb.Layouts do
  @moduledoc """
  This module holds layouts and related functionality
  used by your application.
  """
  use AnalyticsWorkbenchWeb, :html

  embed_templates "layouts/*"

  @doc """
  Renders your app layout.
  """
  slot :inner_block, required: true

  def app(assigns) do
    ~H"""
    <main>
      {render_slot(@inner_block)}
    </main>
    """
  end
end
