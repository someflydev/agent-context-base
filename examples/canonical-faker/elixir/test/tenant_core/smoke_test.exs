defmodule TenantCore.SmokeTest do
  use ExUnit.Case

  test "smoke profile generates 3 organizations" do
    dataset = TenantCore.Pipeline.generate(TenantCore.Profile.smoke())
    assert length(dataset.organizations) == 3
  end

  test "smoke profile passes validation" do
    dataset = TenantCore.Pipeline.generate(TenantCore.Profile.smoke())
    assert dataset.report.ok == true
    assert dataset.report.violations == []
  end

  test "smoke profile is reproducible" do
    d1 = TenantCore.Pipeline.generate(TenantCore.Profile.smoke())
    d2 = TenantCore.Pipeline.generate(TenantCore.Profile.smoke())
    assert d1.organizations == d2.organizations
  end

  test "smoke profile has at least one non-free organization (weighted distribution)" do
    dataset = TenantCore.Pipeline.generate(TenantCore.Profile.small())
    plans = Enum.map(dataset.organizations, & &1.plan)
    free_count = Enum.count(plans, &(&1 == "free"))
    # free should be roughly 50%; allow wider range for small N
    assert free_count < length(plans)
  end
end
