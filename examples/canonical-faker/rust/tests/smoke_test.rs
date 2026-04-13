#[path = "../src/distributions.rs"]
mod distributions;
#[path = "../src/domain.rs"]
mod domain;
#[path = "../src/pipeline.rs"]
mod pipeline;
#[path = "../src/pools.rs"]
mod pools;
#[path = "../src/profiles.rs"]
mod profiles;
#[path = "../src/validate.rs"]
mod validate;

use pipeline::PipelineBuilder;
use profiles::Profile;
use validate::validate;

#[test]
fn test_smoke_produces_correct_org_count() {
    let dataset = PipelineBuilder::new(Profile::SMOKE).build_all().build();
    assert_eq!(dataset.organizations.len(), 3);
}

#[test]
fn test_smoke_passes_validation() {
    let dataset = PipelineBuilder::new(Profile::SMOKE).build_all().build();
    let report = validate(&dataset);
    assert!(report.ok, "Validation failed: {:?}", report.violations);
}

#[test]
fn test_smoke_reproducible() {
    let d1 = PipelineBuilder::new(Profile::SMOKE).build_all().build();
    let d2 = PipelineBuilder::new(Profile::SMOKE).build_all().build();
    assert_eq!(d1.organizations, d2.organizations);
}
