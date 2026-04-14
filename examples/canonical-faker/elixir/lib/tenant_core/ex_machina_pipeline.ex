defmodule TenantCore.ExMachinaPipeline do
  use ExMachina

  def organization_factory do
    %TenantCore.Organization{
      id: Faker.UUID.v4(),
      name: Faker.Company.name(),
      slug: Faker.Internet.slug(),
      plan: Enum.random(["free", "pro", "enterprise"]),
      region: Enum.random(["us-east", "us-west"]),
      created_at: DateTime.utc_now() |> DateTime.to_iso8601(),
      owner_email: sequence(:email, &"user_#{&1}@example.com")
    }
  end

  def user_factory do
    %TenantCore.User{
      id: Faker.UUID.v4(),
      email: sequence(:email, &"user_#{&1}@example.com"),
      full_name: Faker.Person.name(),
      locale: "en-US",
      timezone: "America/New_York",
      created_at: DateTime.utc_now() |> DateTime.to_iso8601()
    }
  end

  # ExMachina provides a factory declaration syntax similar to FactoryBot (Ruby).
  # It handles atomic field generation and simple sequences (unique emails).
  # It does NOT handle relational graph integrity, temporal ordering, or weighted
  # distributions. Those rules must be enforced in the orchestration layer.
  # Use ExMachina for smoke-volume test fixtures. Use TenantCore.Pipeline for
  # production-quality dataset generation.
end
