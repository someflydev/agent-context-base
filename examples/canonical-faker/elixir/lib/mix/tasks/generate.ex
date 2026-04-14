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
    {opts, _, _} = OptionParser.parse(args, 
      strict: [profile: :string, output_dir: :string, format: :string],
      aliases: [o: :output_dir]
    )
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
    
    out_dir = Keyword.get(opts, :output_dir, "./output")
    format = Keyword.get(opts, :format, "jsonl")
    
    if format == "jsonl" do
      File.mkdir_p!(out_dir)
      
      write_jsonl(out_dir, "organizations.jsonl", dataset.organizations)
      write_jsonl(out_dir, "users.jsonl", dataset.users)
      write_jsonl(out_dir, "memberships.jsonl", dataset.memberships)
      write_jsonl(out_dir, "projects.jsonl", dataset.projects)
      write_jsonl(out_dir, "api_keys.jsonl", dataset.api_keys)
      write_jsonl(out_dir, "invitations.jsonl", dataset.invitations)
      write_jsonl(out_dir, "audit_events.jsonl", dataset.audit_events)
    end
  end

  defp write_jsonl(dir, filename, items) do
    path = Path.join(dir, filename)
    content = items
      |> Enum.map(fn item -> Jason.encode!(item) end)
      |> Enum.join("\n")
    File.write!(path, content <> "\n")
    IO.puts("Wrote #{filename}")
  end
end
