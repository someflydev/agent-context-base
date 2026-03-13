require "json"
require "hanami/action"

module RubyHanamiExample
  module Actions
    module Health
      class Show < Hanami::Action
        def handle(_request, response)
          response.format = :json
          response.body = JSON.generate(status: "ok", service: "ruby-hanami-example")
        end
      end
    end
  end
end
