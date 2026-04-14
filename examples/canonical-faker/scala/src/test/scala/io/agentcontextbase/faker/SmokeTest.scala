package io.agentcontextbase.faker

import org.scalatest.flatspec.AnyFlatSpec
import org.scalatest.matchers.should.Matchers

class SmokeTest extends AnyFlatSpec with Matchers {
  "Smoke profile" should "generate 3 organizations" in {
    val dataset = Pipeline.generate(Profile.SMOKE)
    dataset.organizations should have length 3
  }
  
  it should "pass validation" in {
    val dataset = Pipeline.generate(Profile.SMOKE)
    val report = Validate.check(dataset)
    report.ok shouldBe true
    report.violations shouldBe empty
  }
  
  it should "be reproducible" in {
    val d1 = Pipeline.generate(Profile.SMOKE)
    val d2 = Pipeline.generate(Profile.SMOKE)
    d1.organizations shouldBe d2.organizations
  }
}
