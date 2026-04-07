# frozen_string_literal: true

require "json"
require "pathname"
require_relative "job"

module Taskflow
  module Core
    class FixtureError < StandardError; end

    module Loader
      module_function

      def default_fixtures_path
        env_path = ENV["TASKFLOW_FIXTURES_PATH"]
        return Pathname(env_path).expand_path if env_path && !env_path.empty?

        Pathname(__dir__).join("../../../../fixtures").expand_path
      end

      def load_jobs(path = default_fixtures_path)
        load_json(path, "jobs.json").map { |item| Job.from_h(item) }
      end

      def load_config(path = default_fixtures_path)
        load_json(path, "config.json")
      end

      def load_json(path, filename)
        fixtures = Pathname(path).expand_path
        raise FixtureError, "fixtures path does not exist: #{fixtures}" unless fixtures.exist?

        target = fixtures.join(filename)
        raise FixtureError, "missing fixture file: #{target}" unless target.exist?

        JSON.parse(target.read)
      rescue JSON::ParserError => e
        raise FixtureError, "invalid json in #{target}: #{e.message}"
      end
    end
  end
end
