defmodule TenantCore.Output do
  def write_jsonl(_dataset, dir) do
    File.mkdir_p!(dir)
  end
end
