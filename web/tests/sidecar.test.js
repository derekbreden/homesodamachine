// Conformance test for the sidecar contract (web/contracts/sidecar.js).
//
// A .dxf.json / .step.json authored beside a part; read by web/lib/viewer-routes.js and used by
// web/public/js/viewer/dxf.js. Load a real one and assert the fields the viewer relies on carry
// the types it expects, and that sidecarFields surfaces exactly what /api/dxf returns.

import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { sidecarFields } from "../contracts/sidecar.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(__dirname, "..", "..");

function findSidecar(dir) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    if (e.name.startsWith(".") || e.name === "node_modules") continue;
    const full = path.join(dir, e.name);
    if (e.isDirectory()) { const hit = findSidecar(full); if (hit) return hit; }
    else if (e.name.endsWith(".dxf.json") || e.name.endsWith(".step.json")) return full;
  }
  return null;
}

test("a real sidecar conforms, and sidecarFields surfaces the viewer's fields", (t) => {
  const hw = path.join(REPO_ROOT, "hardware");
  const file = fs.existsSync(hw) ? findSidecar(hw) : null;
  if (!file) return t.skip("no sidecar authored yet");
  const meta = JSON.parse(fs.readFileSync(file, "utf8"));

  // The authored fields, when present, are the type the contract names.
  if ("thickness_mm" in meta) assert.equal(typeof meta.thickness_mm, "number", "thickness_mm is a number");
  if ("material" in meta) assert.equal(typeof meta.material, "string", "material is a string");
  if ("process" in meta) assert.equal(typeof meta.process, "string", "process is a string");
  if ("notes" in meta) assert.equal(typeof meta.notes, "string", "notes is a string");

  // The extractor surfaces exactly {thickness_mm, material}, null-safe.
  const f = sidecarFields(meta);
  assert.deepEqual(Object.keys(f).sort(), ["material", "thickness_mm"]);
  assert.ok(f.thickness_mm === null || typeof f.thickness_mm === "number");
  assert.ok(f.material === null || typeof f.material === "string");
  assert.deepEqual(sidecarFields(null), { thickness_mm: null, material: null });
});
