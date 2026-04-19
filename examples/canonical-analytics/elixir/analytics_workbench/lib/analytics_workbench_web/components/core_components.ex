defmodule AnalyticsWorkbenchWeb.CoreComponents do
  @moduledoc """
  Provides core UI components without LiveView or Gettext dependencies.
  """
  use Phoenix.Component

  @doc """
  Renders a button.
  """
  attr :rest, :global, include: ~w(href navigate patch method download name value disabled)
  attr :class, :any, default: nil
  slot :inner_block, required: true

  def button(assigns) do
    ~H"""
    <button class={["btn btn-primary", @class]} {@rest}>
      {render_slot(@inner_block)}
    </button>
    """
  end

  @doc """
  Renders an icon.
  """
  attr :name, :string, required: true
  attr :class, :any, default: "size-4"

  def icon(assigns) do
    ~H"""
    <span class={[@name, @class]} />
    """
  end

  @doc """
  Renders a table.
  """
  attr :id, :string, required: true
  attr :rows, :list, required: true
  slot :col, required: true do
    attr :label, :string
  end

  def table(assigns) do
    ~H"""
    <table class="table w-full">
      <thead>
        <tr>
          <th :for={col <- @col}>{col[:label]}</th>
        </tr>
      </thead>
      <tbody id={@id}>
        <tr :for={row <- @rows}>
          <td :for={col <- @col}>
            {render_slot(col, row)}
          </td>
        </tr>
      </tbody>
    </table>
    """
  end

  @doc """
  Simple error tag.
  """
  slot :inner_block, required: true
  def error(assigns) do
    ~H"""
    <p class="text-sm text-red-600">
      {render_slot(@inner_block)}
    </p>
    """
  end
end
