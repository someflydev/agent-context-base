# frozen_string_literal: true

require "minitest/autorun"
require "pathname"

$LOAD_PATH.unshift(File.expand_path("../../lib", __dir__))

require "taskflow/core/filter"
require "taskflow/core/loader"
require "taskflow/core/stats"

class TaskflowClampCoreTest < Minitest::Test
  def setup
    @fixtures = Pathname(__dir__).join("../../../fixtures").expand_path
    @jobs = Taskflow::Core::Loader.load_jobs(@fixtures)
  end

  def test_load_jobs
    assert_equal 20, @jobs.length
  end

  def test_filter_done_jobs
    done_jobs = Taskflow::Core::Filter.filter(@jobs, status: "done")
    assert done_jobs.all? { |job| job.status == "done" }
  end

  def test_compute_stats
    stats = Taskflow::Core::Stats.compute(@jobs)
    assert_equal 20, stats[:total]
    assert_equal 4, stats[:by_status]["pending"]
  end
end
