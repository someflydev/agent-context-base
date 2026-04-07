# frozen_string_literal: true

require "json"
require "tty-color"
require "tty-table"

module Taskflow
  module CLI
    module Output
      module_function

      def print_jobs(jobs, format: "table", color: false)
        return puts(JSON.pretty_generate(jobs.map(&:to_h))) if format == "json"

        marker_block("## BEGIN_JOBS ##", jobs_table(jobs, color: color), "## END_JOBS ##")
      end

      def print_job(job, format: "plain")
        return puts(JSON.pretty_generate(job.to_h)) if format == "json"

        marker_block("## BEGIN_JOB_DETAIL ##", job_plain(job), "## END_JOB_DETAIL ##")
      end

      def print_stats(stats, format: "plain")
        return puts(JSON.pretty_generate(stats)) if format == "json"

        marker_block("## BEGIN_STATS ##", stats_plain(stats), "## END_STATS ##")
      end

      def print_error(message)
        marker_block("## BEGIN_ERROR ##", message, "## END_ERROR ##")
      end

      def marker_block(begin_marker, content, end_marker)
        puts(begin_marker)
        puts(content) unless content.nil? || content.empty?
        puts(end_marker)
      end

      def jobs_table(jobs, color: false)
        rows = jobs.map do |job|
          [
            job.id,
            job.name,
            color ? color_status(job.status) : job.status,
            job.started_at&.utc&.iso8601 || "-",
            job.tags.join(",")
          ]
        end
        table = TTY::Table.new(header: ["ID", "NAME", "STATUS", "STARTED_AT", "TAGS"], rows: rows)
        table.render(:unicode, multiline: true)
      end

      def job_plain(job)
        [
          "ID: #{job.id}",
          "Name: #{job.name}",
          "Status: #{job.status}",
          "Started: #{job.started_at&.utc&.iso8601 || "-"}",
          "Duration (s): #{job.duration_s || "-"}",
          "Tags: #{job.tags.join(', ')}",
          "Output:",
          *job.output_lines.map { |line| "  - #{line}" }
        ].join("\n")
      end

      def stats_plain(stats)
        [
          "Total jobs: #{stats[:total]}",
          "Done: #{stats[:by_status]['done']}",
          "Failed: #{stats[:by_status]['failed']}",
          "Running: #{stats[:by_status]['running']}",
          "Pending: #{stats[:by_status]['pending']}",
          "Average duration (s): #{stats[:avg_duration_s]}",
          "Failure rate: #{stats[:failure_rate]}"
        ].join("\n")
      end

      def color_status(status)
        return status unless TTY::Color.support?

        case status
        when "done" then "\e[32m#{status}\e[0m"
        when "failed" then "\e[31m#{status}\e[0m"
        when "running" then "\e[33m#{status}\e[0m"
        else "\e[37m#{status}\e[0m"
        end
      end
    end
  end
end
