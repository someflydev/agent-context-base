# frozen_string_literal: true

module Taskflow
  module Core
    module Filter
      module_function

      def filter(jobs, status: nil, tag: nil)
        selected = jobs
        selected = selected.select { |job| job.status == status } if status && !status.empty?
        selected = selected.select { |job| job.tags.include?(tag) } if tag && !tag.empty?
        selected
      end

      def sort(jobs, by: :started_at)
        case by
        when :name
          jobs.sort_by(&:name)
        when :status
          jobs.sort_by { |job| [job.status, job.name] }
        else
          jobs.sort_by { |job| [job.started_at || Time.at(0), job.name] }.reverse
        end
      end
    end
  end
end
