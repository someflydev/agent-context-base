# frozen_string_literal: true

require "tty-color"
require "tty-reader"
require_relative "../core/filter"

module Taskflow
  module Interactive
    class Pager
      def initialize(jobs)
        @all_jobs = jobs
        @visible_jobs = jobs
        @index = 0
        @reader = TTY::Reader.new
      end

      def run
        @reader.raw do
          loop do
            render
            case @reader.read_keypress
            when "q"
              break
            when "\e[A"
              @index = [@index - 1, 0].max
            when "\e[B"
              @index = [@index + 1, @visible_jobs.length - 1].min
            when "f"
              filter_by_status
            end
          end
        end
      end

      private

      def render
        puts "\e[H\e[2J"
        puts "TaskFlow Pager - q=quit, up/down=scroll, f=filter"
        window_start = [@index - 5, 0].max
        @visible_jobs[window_start, 11].to_a.each_with_index do |job, offset|
          absolute_index = window_start + offset
          marker = absolute_index == @index ? ">" : " "
          puts "#{marker} #{job.id} #{job.name.ljust(24)} #{color_status(job.status)}"
        end
      end

      def filter_by_status
        print "\nFilter status (pending/running/done/failed, blank=clear): "
        input = STDIN.gets&.strip
        @visible_jobs = if input.nil? || input.empty?
                          @all_jobs
                        else
                          Taskflow::Core::Filter.filter(@all_jobs, status: input)
                        end
        @visible_jobs = @all_jobs if @visible_jobs.empty?
        @index = 0
      end

      def color_status(status)
        return status unless TTY::Color.support?

        case status
        when "done" then "\e[32m#{status}\e[0m"
        when "failed" then "\e[31m#{status}\e[0m"
        when "running" then "\e[33m#{status}\e[0m"
        else "\e[37m#{status}\e[0m"
        end
      end
    end
  end
end
