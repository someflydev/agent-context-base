ENV["RACK_ENV"] = "test"
ENV["TENANTCORE_TEST_SECRET"] ||= "tenantcore-test-secret"

require "rack/test"

$LOAD_PATH.unshift(File.expand_path("../lib", __dir__))

require "tenantcore_auth/app"
require "tenantcore_auth/domain/in_memory_store"
require "tenantcore_auth/auth/token_service"

RSpec.configure do |config|
  config.include Rack::Test::Methods
  config.order = :random
  Kernel.srand config.seed
end

def app
  TenantcoreAuth::App.rack_app
end
