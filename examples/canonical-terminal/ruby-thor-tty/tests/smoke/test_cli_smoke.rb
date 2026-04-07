# frozen_string_literal: true

require "json"
require "minitest/autorun"
require "open3"
require "pathname"

class TaskflowCliSmokeTest < Minitest::Test
  def setup
    @root = Pathname(__dir__).join("../..").expand_path
    @fixtures = @root.join("../fixtures").expand_path
    @bin = @root.join("bin/taskflow").to_s
    @env = { "TASKFLOW_FIXTURES_PATH" => @fixtures.to_s }
  end

  def test_list_table
    stdout, stderr, status = run_cli("list")
    assert status.success?, stderr
    assert_includes stdout, "## BEGIN_JOBS ##"
    assert_includes stdout, "job-001"
  end

  def test_list_json
    stdout, stderr, status = run_cli("list", "--output", "json")
    assert status.success?, stderr
    payload = JSON.parse(stdout)
    assert_equal 20, payload.length
  end

  def test_filter
    stdout, stderr, status = run_cli("list", "--status", "done", "--output", "json")
    assert status.success?, stderr
    payload = JSON.parse(stdout)
    assert payload.all? { |job| job["status"] == "done" }
  end

  def test_inspect
    stdout, stderr, status = run_cli("inspect", "job-001", "--output", "json")
    assert status.success?, stderr
    payload = JSON.parse(stdout)
    assert_equal "job-001", payload["id"]
  end

  def test_stats
    stdout, stderr, status = run_cli("stats", "--output", "json")
    assert status.success?, stderr
    payload = JSON.parse(stdout)
    assert_equal 20, payload["total"]
  end

  def test_watch_batch
    stdout, stderr, status = run_cli("watch", "--no-interactive")
    assert status.success?, stderr
    assert_includes stdout, "## BEGIN_JOBS ##"
  end

  def test_missing
    stdout, stderr, status = run_cli("list", "--fixtures-path", @root.join("missing").to_s)
    refute status.success?
    assert_includes stdout + stderr, "fixtures path does not exist"
  end

  private

  def run_cli(*args)
    Open3.capture3(@env, "ruby", @bin, *args, chdir: @root.to_s)
  end
end
