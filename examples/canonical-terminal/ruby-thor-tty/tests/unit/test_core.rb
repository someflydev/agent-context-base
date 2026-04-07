# frozen_string_literal: true

require "json"
require "minitest/autorun"
require "pathname"

$LOAD_PATH.unshift(File.expand_path("../../lib", __dir__))

require "taskflow/core/filter"
require "taskflow/core/loader"
require "taskflow/core/stats"

class TaskflowCoreTest < Minitest::Test
  def setup
    @fixtures = Pathname(__dir__).join("../../../fixtures").expand_path
    @jobs = Taskflow::Core::Loader.load_jobs(@fixtures)
  end

  def test_loads_shared_fixture_jobs
    assert_equal 20, @jobs.length
    assert_equal "job-001", @jobs.first.id
  end

  def test_filters_by_status_and_tag
    done_jobs = Taskflow::Core::Filter.filter(@jobs, status: "done")
    assert done_jobs.all? { |job| job.status == "done" }

    tagged = Taskflow::Core::Filter.filter(@jobs, tag: "etl")
    assert tagged.all? { |job| job.tags.include?("etl") }
  end

  def test_computes_stats
    stats = Taskflow::Core::Stats.compute(@jobs)

    assert_equal 20, stats[:total]
    assert_equal 4, stats[:by_status]["failed"]
    assert_in_delta 0.2, stats[:failure_rate], 0.001
  end
end
