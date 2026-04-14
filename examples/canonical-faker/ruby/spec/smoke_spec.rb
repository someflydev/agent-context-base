require_relative '../lib/faker_pipeline'
require_relative '../lib/validate'

describe "TenantCore Faker Pipeline" do
  let(:dataset) { FakerPipeline.generate(Profile::SMOKE) }

  it "generates 3 organizations" do
    expect(dataset[:organizations].length).to eq(3)
  end

  it "passes validation" do
    report = Validate.check(dataset)
    expect(report.ok).to be true
    expect(report.violations).to be_empty
  end

  it "is reproducible" do
    d1 = FakerPipeline.generate(Profile::SMOKE)
    d2 = FakerPipeline.generate(Profile::SMOKE)
    expect(d1[:organizations]).to eq(d2[:organizations])
  end

  it "has skewed plan distribution (not perfectly uniform)" do
    dataset = FakerPipeline.generate(Profile::SMALL)
    plans = dataset[:organizations].map { |o| o.plan }
    free_count = plans.count("free")
    expect(free_count.to_f / plans.length).to be_between(0.30, 0.75)
  end
end