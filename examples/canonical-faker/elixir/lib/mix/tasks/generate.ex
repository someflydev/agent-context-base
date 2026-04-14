defmodule Mix.Tasks.Generate do
  use Mix.Task

  @shortdoc "Generate TenantCore synthetic dataset"
  @moduledoc """
  Usage:
    mix generate [--profile smoke|small|medium|large]
                 [--output ./output]
                 [--format jsonl|csv]
  """

  @impl Mix.Task
  def run(args) do
    {opts, _, _} = OptionParser.parse(args, switches: [profile: :string, output: :string, format: :string])
    profile_name = Keyword.get(opts, :profile, "smoke")
    
    profile = case profile_name do
      "smoke" -> TenantCore.Profile.smoke()
      "small" -> TenantCore.Profile.small()
      "medium" -> TenantCore.Profile.medium()
      "large" -> TenantCore.Profile.large()
      _ -> TenantCore.Profile.smoke()
    end
    
    IO.puts("Generating profile #{profile.name}...")
    dataset = TenantCore.Pipeline.generate(profile)
    IO.puts("Validation OK: #{dataset.report.ok}")
    
    out_dir = Keyword.get(opts, :output, "./output")
    format = Keyword.get(opts, :format, "jsonl")
    
    if format == "jsonl" do
      File.mkdir_p!(out_dir)
      File.write!(Path.join(out_dir, "organizations.jsonl"), "")
    end
  end
end
