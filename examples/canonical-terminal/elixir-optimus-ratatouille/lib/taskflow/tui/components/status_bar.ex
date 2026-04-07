defmodule Taskflow.Tui.Components.StatusBar do
  import Ratatouille.View

  def render(stats) do
    label(
      content:
        "total=#{stats.total} pending=#{stats.by_status["pending"]} " <>
          "running=#{stats.by_status["running"]} done=#{stats.by_status["done"]} failed=#{stats.by_status["failed"]}"
    )
  end
end
