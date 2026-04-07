# frozen_string_literal: true

require "time"

module Taskflow
  module Core
    Job = Struct.new(:id, :name, :status, :started_at, :duration_s, :tags, :output_lines, keyword_init: true) do
      def self.from_h(payload)
        new(
          id: payload.fetch("id"),
          name: payload.fetch("name"),
          status: payload.fetch("status"),
          started_at: payload["started_at"] ? Time.iso8601(payload["started_at"]).utc : nil,
          duration_s: payload["duration_s"],
          tags: Array(payload["tags"]),
          output_lines: Array(payload["output_lines"])
        )
      end

      def to_h
        {
          id: id,
          name: name,
          status: status,
          started_at: started_at&.utc&.iso8601,
          duration_s: duration_s,
          tags: tags,
          output_lines: output_lines
        }
      end
    end
  end
end
