// Runtime admission for direct Node/Bun heavy entrypoints.
import path from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";

let runAdmitted = false;
export function ensureRunLease() {
  if (runAdmitted) return;
  const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
  const runner = path.join(root, "tools/run");
  // The private broker transfers real held descriptors; an environment marker is no proof.
  const checked = spawnSync(runner, ["--check-inherited"], { stdio: "ignore" });
  if (checked.status === 0) {
    runAdmitted = true;
    return;
  }
  const child = spawnSync(runner,
    ["--", process.execPath, ...process.execArgv, ...process.argv.slice(1)],
    { stdio: "inherit" });
  if (child.error) throw child.error;
  process.exit(child.status ?? 1);
}
