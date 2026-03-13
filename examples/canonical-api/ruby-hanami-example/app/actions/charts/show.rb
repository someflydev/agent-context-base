require "json"
require "hanami/action"

require_relative "../../../lib/ruby_hanami_example/persistence"

module RubyHanamiExample
  module Actions
    module Charts
      class Show < Hanami::Action
        def handle(request, response)
          metric = request.params[:metric].to_s

          response.format = :json
          response.body = JSON.generate(
            metric: metric,
            series: [
              {
                name: metric,
                points: RubyHanamiExample::Persistence.series_for(metric),
              },
            ],
          )
        end
      end
    end
  end
end
