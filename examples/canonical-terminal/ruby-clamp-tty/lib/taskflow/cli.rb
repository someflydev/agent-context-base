# frozen_string_literal: true

require "clamp"
require "json"
require "pathname"
require "tty-color"
require_relative "core/filter"
require_relative "core/loader"
require_relative "core/stats"
require_relative "interactive/pager"

module Taskflow
  module CLI
    module_function

    def run(argv)
      TaskflowCommand.run(argv)
    rescue Taskflow::Core::FixtureError => e
      print_error(e.message)
      exit(1)
    end

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
      puts begin_marker
      puts content unless content.nil? || content.empty?
      puts end_marker
    end

    def jobs_table(jobs, color: false)
      header = format("%-8s %-24s %-8s %-20s %s", "ID", "NAME", "STATUS", "STARTED_AT", "TAGS")
      rows = jobs.map do |job|
        status = color ? color_status(job.status) : job.status
        format("%-8s %-24s %-8s %-20s %s", job.id, job.name, status, job.started_at&.utc&.iso8601 || "-", job.tags.join(","))
      end
      ([header] + rows).join("\n")
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

    class BaseCommand < Clamp::Command
      option ["--fixtures-path"], "PATH", "Fixture directory"

      def resolved_fixtures_path
        return Pathname(fixtures_path).expand_path if fixtures_path && !fixtures_path.empty?

        Taskflow::Core::Loader.default_fixtures_path
      end

      def jobs
        Taskflow::Core::Filter.sort(Taskflow::Core::Loader.load_jobs(resolved_fixtures_path))
      end
    end

    class ListCommand < BaseCommand
      option ["--status"], "STATUS", "Filter by status"
      option ["--tag"], "TAG", "Filter by tag"
      option ["--output"], "FORMAT", "table or json", default: "table"

      def execute
        filtered = Taskflow::Core::Filter.filter(jobs, status: status, tag: tag)
        Taskflow::CLI.print_jobs(filtered, format: output)
      end
    end

    class InspectCommand < BaseCommand
      parameter "JOB_ID", "Job identifier"
      option ["--output"], "FORMAT", "plain or json", default: "plain"

      def execute
        job = jobs.find { |item| item.id == job_id }
        raise Taskflow::Core::FixtureError, "job not found: #{job_id}" unless job

        Taskflow::CLI.print_job(job, format: output)
      end
    end

    class StatsCommand < BaseCommand
      option ["--output"], "FORMAT", "plain or json", default: "plain"

      def execute
        Taskflow::CLI.print_stats(Taskflow::Core::Stats.compute(jobs), format: output)
      end
    end

    class WatchCommand < BaseCommand
      option ["--no-interactive"], :flag, "Run in headless mode"

      def execute
        return Taskflow::CLI.print_jobs(jobs, format: "table") if no_interactive?

        Taskflow::Interactive::Pager.new(jobs).run
      end
    end

    class TaskflowCommand < Clamp::Command
      subcommand "list", "List jobs", ListCommand
      subcommand "inspect", "Show job details", InspectCommand
      subcommand "stats", "Show queue statistics", StatsCommand
      subcommand "watch", "Monitor queue", WatchCommand
    end
  end
end
