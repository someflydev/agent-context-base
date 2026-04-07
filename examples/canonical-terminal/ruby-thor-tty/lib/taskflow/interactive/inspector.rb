# frozen_string_literal: true

require "tty-prompt"
require_relative "../core/filter"
require_relative "../core/loader"
require_relative "../core/stats"
require_relative "../cli/output"

module Taskflow
  module Interactive
    class Inspector
      def initialize(fixtures_path)
        @fixtures_path = fixtures_path
        @prompt = TTY::Prompt.new
      end

      def run
        loop do
          jobs = Taskflow::Core::Filter.sort(Taskflow::Core::Loader.load_jobs(@fixtures_path))
          action = @prompt.select("TaskFlow Inspector", [
                                    "List all jobs",
                                    "Filter by status",
                                    "Inspect a job",
                                    "Show stats",
                                    "Quit"
                                  ])
          case action
          when "List all jobs"
            puts(Taskflow::CLI::Output.jobs_table(jobs, color: true))
          when "Filter by status"
            status = @prompt.select("Select status:", %w[pending running done failed])
            filtered = Taskflow::Core::Filter.filter(jobs, status: status)
            puts(Taskflow::CLI::Output.jobs_table(filtered, color: true))
          when "Inspect a job"
            job_id = @prompt.ask("Enter job ID (e.g. job-001):")
            job = jobs.find { |item| item.id == job_id }
            job ? puts(Taskflow::CLI::Output.job_plain(job)) : @prompt.warn("Job not found: #{job_id}")
          when "Show stats"
            puts(Taskflow::CLI::Output.stats_plain(Taskflow::Core::Stats.compute(jobs)))
          when "Quit"
            break
          end
          @prompt.keypress("Press any key to continue...")
        end
      end
    end
  end
end
