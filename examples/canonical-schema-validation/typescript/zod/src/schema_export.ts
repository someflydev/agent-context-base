/*
Lane C demonstration: one Zod schema definition yields a TypeScript type
(static), a runtime validator, and a JSON Schema (contract).
*/

import Ajv from "ajv";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { zodToJsonSchema } from "zod-to-json-schema";

import { WorkspaceConfigSchema } from "./models.js";

const here = dirname(fileURLToPath(import.meta.url));
const fixtures = join(here, "../../../domain/fixtures");
const ajv = new Ajv();

const validFixture = JSON.parse(readFileSync(join(fixtures, "valid/workspace_config_full.json"), "utf-8"));
const invalidFixture = JSON.parse(readFileSync(join(fixtures, "invalid/workspace_config_bad_slug.json"), "utf-8"));
const workspaceConfigJsonSchema = zodToJsonSchema(WorkspaceConfigSchema, "WorkspaceConfig");

console.log(JSON.stringify(workspaceConfigJsonSchema, null, 2));
JSON.parse(JSON.stringify(workspaceConfigJsonSchema));

const validate = ajv.compile(workspaceConfigJsonSchema);
if (!validate(validFixture)) {
  throw new Error(`valid fixture unexpectedly failed: ${JSON.stringify(validate.errors)}`);
}
if (validate(invalidFixture)) {
  throw new Error("invalid fixture unexpectedly passed exported JSON Schema");
}

console.log("schema export and drift checks passed");
