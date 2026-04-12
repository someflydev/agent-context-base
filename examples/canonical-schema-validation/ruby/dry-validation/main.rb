require "json"

require_relative "contracts/workspace_config_contract"
require_relative "contracts/sync_run_contract"
require_relative "contracts/webhook_payload_contract"
require_relative "contracts/ingestion_source_contract"
require_relative "contracts/review_request_contract"

FIXTURE_ROOT = File.expand_path("../../domain/fixtures", __dir__)

def load_fixture(path)
  JSON.parse(File.read(File.join(FIXTURE_ROOT, path)), symbolize_names: true)
end

def run_contract(name, contract, fixture, expect_pass:)
  result = contract.call(load_fixture(fixture))
  if expect_pass
    puts(result.errors.empty? ? "#{name} #{fixture} PASS" : "#{name} #{fixture} FAIL: #{result.errors.to_h}")
  else
    puts(result.errors.empty? ? "#{name} #{fixture} UNEXPECTED_PASS" : "#{name} #{fixture} FAIL: #{result.errors.to_h}")
  end
end

run_contract("workspace", WorkspaceConfigContract.new, "valid/workspace_config_basic.json", expect_pass: true)
run_contract("workspace", WorkspaceConfigContract.new, "invalid/workspace_config_bad_slug.json", expect_pass: false)
run_contract("workspace", WorkspaceConfigContract.new, "invalid/workspace_config_plan_too_many_runs.json", expect_pass: false)
run_contract("sync_run", SyncRunContract.new, "valid/sync_run_pending.json", expect_pass: true)
run_contract("sync_run", SyncRunContract.new, "invalid/sync_run_timestamps_inverted.json", expect_pass: false)
run_contract("review_request", ReviewRequestContract.new, "invalid/review_request_critical_no_due_date.json", expect_pass: false)
