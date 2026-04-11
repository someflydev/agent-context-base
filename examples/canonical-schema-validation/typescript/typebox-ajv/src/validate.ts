import Ajv from "ajv";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { WorkspaceConfigSchema } from "./schemas.js";

// The TypeBox schema IS a JSON Schema object. No transformation needed. This is
// the contract-first lane: the schema is the source of truth for both validation
// (Ajv) and contract export (JSON Schema spec).
const ajv = new Ajv();
const validate = ajv.compile(WorkspaceConfigSchema);

const here = dirname(fileURLToPath(import.meta.url));
const fixtures = join(here, "../../../domain/fixtures");
const validFixture = JSON.parse(readFileSync(join(fixtures, "valid/workspace_config_full.json"), "utf-8"));
const invalidFixture = JSON.parse(readFileSync(join(fixtures, "invalid/workspace_config_bad_slug.json"), "utf-8"));

console.log(JSON.stringify(WorkspaceConfigSchema, null, 2));
console.log("valid fixture:", validate(validFixture));
console.log("invalid fixture:", validate(invalidFixture));
