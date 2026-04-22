$LOAD_PATH.unshift(File.expand_path("lib", __dir__))

require "tenantcore_auth/app"

run TenantcoreAuth::App.rack_app
