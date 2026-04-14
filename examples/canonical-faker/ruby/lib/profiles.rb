class Profile
  attr_reader :name, :num_orgs, :num_users, :seed

  def initialize(name, num_orgs, num_users, seed)
    @name = name
    @num_orgs = num_orgs
    @num_users = num_users
    @seed = seed
  end

  SMOKE = Profile.new("smoke", 3, 10, 42).freeze
  SMALL = Profile.new("small", 20, 200, 1000).freeze
  MEDIUM = Profile.new("medium", 200, 5000, 5000).freeze
  LARGE = Profile.new("large", 2000, 50000, 9999).freeze

  def self.from_name(name)
    case name
    when "smoke" then SMOKE
    when "small" then SMALL
    when "medium" then MEDIUM
    when "large" then LARGE
    else SMOKE
    end
  end
end