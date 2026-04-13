import { resolve } from "node:path"
import { PROFILES } from "./profiles.js"
import { generateAndWrite } from "./pipeline.js"

async function main(): Promise<number> {
  const profileArg = process.argv[2] ?? "smoke"
  const formatArg = (process.argv[3] ?? "jsonl") as "jsonl" | "csv"
  const outputBase = resolve(process.argv[4] ?? "./output")
  const profile = PROFILES[profileArg]
  if (!profile) {
    console.error("Usage: npx ts-node src/index.ts [smoke|small|medium|large] [jsonl|csv] [output-dir]")
    return 1
  }
  if (formatArg !== "jsonl" && formatArg !== "csv") {
    console.error("Format must be jsonl or csv")
    return 1
  }
  const { report } = await generateAndWrite(profile, formatArg, resolve(outputBase, profile.name))
  console.log(JSON.stringify(report, null, 2))
  return report.ok ? 0 : 1
}

main().then(
  (code) => {
    process.exitCode = code
  },
  (error: unknown) => {
    console.error(error)
    process.exitCode = 1
  }
)
