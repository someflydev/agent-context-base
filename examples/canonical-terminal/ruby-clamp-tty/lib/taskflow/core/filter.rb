# frozen_string_literal: true

module Taskflow
  module Core
    module Filter
      module_function

      def filter(jobs, status: nil, tag: nil)
        filtered = jobs
        filtered = filtered.select { |job| job.status == status } if status && !status.empty?
        filtered = filtered.select { |job| job.tags.include?(tag) } if tag && !tag.empty?
        filtered
      end

      def sort(jobs)
        jobs.sort_by { |job| [job.started_at || Time.at(0), job.name] }.reverse
      end
    end
  end
end
