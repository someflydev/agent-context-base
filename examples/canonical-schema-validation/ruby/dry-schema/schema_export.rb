require "json"

require_relative "schemas/workspace_config_schema"

schema_hash =
  if WorkspaceConfigSchema.respond_to?(:json_schema)
    WorkspaceConfigSchema.json_schema
  else
    {
      "$comment" => "dry-schema JSON Schema extension unavailable; manual structural export",
      "title" => "WorkspaceConfig",
      "type" => "object",
      "properties" => WorkspaceConfigSchema.key_map.to_dot_notation.each_with_object({}) do |key, acc|
        acc[key] = { "type" => "unknown" }
      end,
    }
  end

puts JSON.pretty_generate(schema_hash)
