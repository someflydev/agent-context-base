# frozen_string_literal: true

require "thor"
require_relative "../core/filter"
require_relative "../core/loader"
require_relative "../core/stats"
require_relative "output"
require_relative "../interactive/inspector"

module Taskflow
  module CLI
    class Commands < Thor
      def self.exit_on_failure?
        true
      end

      desc "list", "List jobs"
      option :status, type: :string
      option :tag, type: :string
      option :output, type: :string, default: "table", enum: %w[table json]
      option :fixtures_path, type: :string, aliases: "-f"
      def list
        jobs = load_and_filter(options)
        Output.print_jobs(jobs, format: options[:output])
      rescue Taskflow::Core::FixtureError => e
        abort_with_error(e.message)
      end

      desc "inspect JOB_ID", "Show job details"
      option :output, type: :string, default: "plain", enum: %w[plain json]
      option :fixtures_path, type: :string, aliases: "-f"
      def inspect(job_id)
        job = load_jobs.find { |item| item.id == job_id }
        raise Taskflow::Core::FixtureError, "job not found: #{job_id}" unless job

        Output.print_job(job, format: options[:output])
      rescue Taskflow::Core::FixtureError => e
        abort_with_error(e.message)
      end

      desc "stats", "Show queue statistics"
      option :output, type: :string, default: "plain", enum: %w[plain json]
      option :fixtures_path, type: :string, aliases: "-f"
      def stats
        Output.print_stats(Taskflow::Core::Stats.compute(load_jobs), format: options[:output])
      rescue Taskflow::Core::FixtureError => e
        abort_with_error(e.message)
      end

      desc "watch", "Monitor queue (interactive or batch)"
      option :"no-interactive", type: :boolean, default: false
      option :fixtures_path, type: :string, aliases: "-f"
      def watch
        if options[:"no-interactive"]
          Output.print_jobs(Taskflow::Core::Filter.sort(load_jobs), format: "table")
        else
          Taskflow::Interactive::Inspector.new(fixtures_path).run
        end
      rescue Taskflow::Core::FixtureError => e
        abort_with_error(e.message)
      end

      no_commands do
        def fixtures_path
          path = options[:fixtures_path]
          path && !path.empty? ? path : Taskflow::Core::Loader.default_fixtures_path
        end

        def load_jobs
          Taskflow::Core::Loader.load_jobs(fixtures_path)
        end

        def load_and_filter(opts)
          jobs = Taskflow::Core::Loader.load_jobs(fixtures_path)
          Taskflow::Core::Filter.sort(
            Taskflow::Core::Filter.filter(jobs, status: opts[:status], tag: opts[:tag])
          )
        end

        def abort_with_error(message)
          Output.print_error(message)
          raise Thor::Error, message
        end
      end
    end
  end
end
