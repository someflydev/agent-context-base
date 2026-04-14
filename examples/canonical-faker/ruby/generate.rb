#!/usr/bin/env ruby
require 'optparse'
require 'json'
require 'csv'
require 'fileutils'
require_relative 'lib/faker_pipeline'
require_relative 'lib/ffaker_pipeline'
require_relative 'lib/validate'

options = {
  pipeline: 'faker',
  profile: 'smoke',
  output: './output',
  format: 'jsonl'
}

OptionParser.new do |opts|
  opts.banner = "Usage: ruby generate.rb [--pipeline faker|ffaker] [--profile smoke|small|medium|large] [--output ./output] [--format jsonl|csv]"

  opts.on("--pipeline P", String, "Pipeline to use: faker or ffaker") do |p|
    options[:pipeline] = p
  end
  opts.on("--profile P", String, "Profile to use: smoke, small, medium, large") do |p|
    options[:profile] = p
  end
  opts.on("--output D", String, "Output directory") do |d|
    options[:output] = d
  end
  opts.on("--format F", String, "Output format: jsonl or csv") do |f|
    options[:format] = f
  end
end.parse!

profile = Profile.from_name(options[:profile])

if options[:pipeline] == 'ffaker'
  dataset = FfakerPipeline.generate(profile)
else
  dataset = FakerPipeline.generate(profile)
end

FileUtils.mkdir_p(options[:output])

dataset.each do |entity, rows|
  next if rows.empty?

  file_ext = options[:format] == 'csv' ? 'csv' : 'jsonl'
  path = File.join(options[:output], "#{entity}.#{file_ext}")
  
  if file_ext == 'jsonl'
    File.open(path, 'w') do |f|
      rows.each do |row|
        f.puts(entity_to_hash(row).to_json)
      end
    end
  else
    CSV.open(path, 'w') do |csv|
      headers = entity_to_hash(rows.first).keys
      csv << headers
      rows.each do |row|
        csv << entity_to_hash(row).values
      end
    end
  end
end

if options[:pipeline] == 'faker'
  report = Validate.check(dataset)
  Validate.print_report(report)
  exit(report.ok ? 0 : 1)
else
  puts "FFaker pipeline ran successfully (Organizations only)."
  exit 0
end