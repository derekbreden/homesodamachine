// The mesh payload's version, held across the three files that state it.
//
// A payload is written by hardware/scripts/_mesh_payload.py and read by
// web/public/js/viewer/step.js, which are different languages in different trees
// with no import between them. Each states the versions it can take, and
// hardware/scripts/check_payloads.py states the one a committed payload has to
// carry. Nothing else makes them agree.
//
// WHAT DISAGREEMENT COSTS IS SILENCE. `decodeMeshPayload` answers a version it
// does not know with `null`, `fetchMeshes` reads that as no payload, and
// `loadStepFile` parses the STEP instead — the right picture, thirteen seconds
// later. Under `pack.BUNDLED_PAYLOAD_DIRS` it is not even the right picture: the
// flutes live in the payload and never in the STEP, so the appliance renders as a
// smooth box. Nothing throws, and no page says so.
//
// Read as text, because that is the only thing JavaScript and Python share here.

import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..", "..");

const read = (rel) => fs.readFileSync(path.join(ROOT, rel), "utf8");

// `[2, 3]` / `(2, 3)` -> [2, 3], from whichever language wrote it.
function numbers(text, re, what) {
  const m = re.exec(text);
  assert.ok(m, `${what} states no version`);
  return m[1].split(",").map((s) => Number(s.trim())).filter((n) => !Number.isNaN(n));
}

test("the page decodes every version the writer stamps", () => {
  const py = read("hardware/scripts/_mesh_payload.py");
  const js = read("web/public/js/viewer/step.js");

  const written = numbers(py, /^VERSION = (\d+)/m, "_mesh_payload.VERSION");
  const decodable = numbers(py, /^DECODABLE = \(([^)]*)\)/m, "_mesh_payload.DECODABLE");
  const pageReads = numbers(js, /const MESH_PAYLOAD_VERSIONS = \[([^\]]*)\]/, "step.js");

  // The writer's own version is one the writer says is decodable.
  assert.ok(decodable.includes(written[0]),
    `_mesh_payload writes ${written[0]}, which its own DECODABLE ${JSON.stringify(decodable)} does not name`);

  // And the page takes exactly that set. Wider on the page alone would be a
  // version nothing writes; narrower is a payload the page turns away.
  assert.deepEqual([...pageReads].sort(), [...decodable].sort(),
    "step.js's MESH_PAYLOAD_VERSIONS and _mesh_payload.DECODABLE state different sets");
});

test("the payload gate holds the version the writer stamps", () => {
  const py = read("hardware/scripts/_mesh_payload.py");
  const gate = read("hardware/scripts/check_payloads.py");

  const written = numbers(py, /^VERSION = (\d+)/m, "_mesh_payload.VERSION");
  const held = numbers(gate, /^PAYLOAD_VERSION = (\d+)/m, "check_payloads.PAYLOAD_VERSION");

  assert.deepEqual(held, written,
    `check_payloads holds ${held[0]} and _mesh_payload writes ${written[0]}`);
});
