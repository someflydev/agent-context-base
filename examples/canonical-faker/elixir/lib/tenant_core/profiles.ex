defmodule TenantCore.Profile do
  defstruct [:name, :seed, :num_orgs, :num_users]

  def smoke do
    %__MODULE__{name: "smoke", seed: 42, num_orgs: 3, num_users: 10}
  end

  def small do
    %__MODULE__{name: "small", seed: 42, num_orgs: 10, num_users: 50}
  end

  def medium do
    %__MODULE__{name: "medium", seed: 42, num_orgs: 100, num_users: 500}
  end

  def large do
    %__MODULE__{name: "large", seed: 42, num_orgs: 1000, num_users: 5000}
  end
end
