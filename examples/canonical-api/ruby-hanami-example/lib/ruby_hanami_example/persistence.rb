require "sequel"

module RubyHanamiExample
  module Persistence
    class << self
      def report_for(tenant_id)
        prepare!
        row = reports.where(tenant_id: tenant_id).first || default_report
        {
          report_id: row[:report_id],
          total_events: row[:total_events],
          status: row[:status],
        }
      end

      def series_for(metric)
        prepare!
        rows = metric_points.where(metric: metric).order(:bucket_day).all
        rows = default_metric_rows(metric) if rows.empty?
        rows.map { |row| { x: row[:bucket_day], y: row[:total] } }
      end

      private

      def db
        @db ||= Sequel.sqlite
      end

      def reports
        db[:reports]
      end

      def metric_points
        db[:metric_points]
      end

      def prepare!
        return if @prepared

        db.create_table?(:reports) do
          primary_key :id
          String :tenant_id, null: false
          String :report_id, null: false
          Integer :total_events, null: false
          String :status, null: false
        end

        db.create_table?(:metric_points) do
          primary_key :id
          String :metric, null: false
          String :bucket_day, null: false
          Integer :total, null: false
        end

        seed!
        @prepared = true
      end

      def seed!
        return unless reports.count.zero? && metric_points.count.zero?

        reports.insert(
          tenant_id: "acme",
          report_id: "daily-signups",
          total_events: 42,
          status: "ready",
        )
        reports.insert(
          tenant_id: "globex",
          report_id: "ops-latency",
          total_events: 17,
          status: "warming",
        )

        metric_points.multi_insert(
          [
            { metric: "signups", bucket_day: "2026-03-01", total: 18 },
            { metric: "signups", bucket_day: "2026-03-02", total: 24 },
            { metric: "signups", bucket_day: "2026-03-03", total: 31 },
          ],
        )
      end

      def default_report
        {
          report_id: "daily-signups",
          total_events: 42,
          status: "ready",
        }
      end

      def default_metric_rows(metric)
        [
          { metric: metric, bucket_day: "2026-03-01", total: 18 },
          { metric: metric, bucket_day: "2026-03-02", total: 24 },
          { metric: metric, bucket_day: "2026-03-03", total: 31 },
        ]
      end
    end
  end
end
