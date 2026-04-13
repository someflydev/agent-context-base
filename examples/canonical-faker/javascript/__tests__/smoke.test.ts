import { generateDataset } from "../src/pipeline.js"
import { SMALL, SMOKE } from "../src/profiles.js"
import { validateDataset } from "../src/validate.js"

describe("TenantCoreSmokeTests", () => {
  test("generates smoke profile organizations", async () => {
    const dataset = await generateDataset(SMOKE)
    expect(dataset.organizations).toHaveLength(3)
  })

  test("smoke profile produces valid FK integrity", async () => {
    const dataset = await generateDataset(SMOKE)
    const report = validateDataset(dataset)
    expect(report.ok).toBe(true)
    expect(report.violations).toHaveLength(0)
  })

  test("smoke profile is reproducible", async () => {
    const left = await generateDataset(SMOKE)
    const right = await generateDataset(SMOKE)
    expect(left.organizations).toEqual(right.organizations)
    expect(left.auditEvents).toEqual(right.auditEvents)
  })

  test("generates at least one non-uniform distribution", async () => {
    const dataset = await generateDataset(SMALL)
    const plans = dataset.organizations.map((row) => row.plan)
    const freePct = plans.filter((plan) => plan === "free").length / plans.length
    expect(freePct).toBeGreaterThan(0.25)
    expect(freePct).toBeLessThan(0.8)
  })
})
