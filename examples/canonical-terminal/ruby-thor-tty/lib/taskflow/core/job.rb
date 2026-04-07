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
          started_at: parse_time(payload["started_at"]),
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
          started_at: self.class.format_time(started_at),
          duration_s: duration_s,
          tags: tags,
          output_lines: output_lines
        }
      end

      def self.parse_time(value)
        value.nil? ? nil : Time.iso8601(value).utc
      end

      def self.format_time(value)
        value&.utc&.iso8601
      end
    end

    Event = Struct.new(:event_id, :job_id, :event_type, :timestamp, :message, keyword_init: true) do
      def self.from_h(payload)
        new(
          event_id: payload.fetch("event_id"),
          job_id: payload.fetch("job_id"),
          event_type: payload.fetch("event_type"),
          timestamp: Time.iso8601(payload.fetch("timestamp")).utc,
          message: payload.fetch("message")
        )
      end

      def to_h
        {
          event_id: event_id,
          job_id: job_id,
          event_type: event_type,
          timestamp: timestamp.utc.iso8601,
          message: message
        }
      end
    end
  end
end
