# frozen_string_literal: true

module Taskflow
  module Core
    module Stats
      module_function

      def compute(jobs)
        counts = %w[pending running done failed].to_h { |status| [status, 0] }
        durations = []

        jobs.each do |job|
          counts[job.status] += 1 if counts.key?(job.status)
          durations << job.duration_s if job.duration_s
        end

        total = jobs.length
        {
          total: total,
          by_status: counts,
          avg_duration_s: durations.empty? ? 0.0 : (durations.sum / durations.length).round(2),
          failure_rate: total.zero? ? 0.0 : (counts["failed"].to_f / total).round(2)
        }
      end
    end
  end
end
