import { isLeft } from "fp-ts/lib/Either.js";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { WorkspaceConfigCodec, decodeSyncRun } from "./codecs.ts";

const here = dirname(fileURLToPath(import.meta.url));
const fixtures = join(here, "../../../domain/fixtures");

const validWorkspace = JSON.parse(
  readFileSync(join(fixtures, "valid/workspace_config_full.json"), "utf-8"),
);
const invalidSyncRun = JSON.parse(
  readFileSync(
    join(fixtures, "invalid/sync_run_duration_missing_when_finished.json"),
    "utf-8",
  ),
);

const workspaceResult = WorkspaceConfigCodec.decode(validWorkspace);
if (isLeft(workspaceResult)) {
  throw new Error("valid workspace fixture unexpectedly failed io-ts decode");
}

const syncRunResult = decodeSyncRun(invalidSyncRun);
if (!isLeft(syncRunResult)) {
  throw new Error("invalid sync run fixture unexpectedly passed io-ts decode");
}

console.log("io-ts smoke checks passed");
