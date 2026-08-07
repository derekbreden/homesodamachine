// port-format unit tests — the two shapes scorecard.py's Port.face takes.
//
// The regression: the marker overlay knew only the six body-face names and fell back
// to [0, 0, 1] for anything else, so every port whose face is a vector — the rolled
// elbows, the tees hung between them, the pumps, the bag circuit — was drawn pointing
// straight up. Two of them (Y-E-2, V-F-I) are dead horizontal in the model. The last
// test reads the committed sidecar, so it fails if a vector face stops being read.

import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { faceNormal, faceLabel } from "../public/js/viewer/port-format.js";

const _here = path.dirname(fileURLToPath(import.meta.url));
// The live pack's sidecar. The enclosure-assembly's is a retired output — nothing
// rebuilds it — so the audit follows the machine to hardware/manifold-layout/, and
// skips itself until front_half writes one.
const SIDECAR = path.join(
  _here, "..", "..", "hardware", "manifold-layout", "front-half.scorecard.json",
);

test("named body faces read as their outward normal", () => {
  assert.deepEqual(faceNormal("z+"), [0, 0, 1]);
  assert.deepEqual(faceNormal("z-"), [0, 0, -1]);
  assert.deepEqual(faceNormal("x-"), [-1, 0, 0]);
  assert.deepEqual(faceNormal("y+"), [0, 1, 0]);
});

test("a vector face reads as itself, normalized", () => {
  // Y-H-2's own axis: 9.2 deg off vertical, tilted aft.
  const n = faceNormal([-0.0, 0.15922473595015468, -0.9872423630809223]);
  assert.ok(Math.abs(Math.hypot(...n) - 1) < 1e-12, "unit length");
  assert.ok(n[2] < -0.98 && n[1] > 0.15, "points down and aft, not up");
  // An unnormalized vector normalizes rather than being taken at face value.
  const m = faceNormal([0, 0, 5]);
  assert.deepEqual(m, [0, 0, 1]);
});

test("an axis-aligned vector face is NOT mistaken for up", () => {
  // The worst of the regression: faces stored as vectors that happen to be
  // axis-aligned, drawn vertical when they are horizontal.
  assert.deepEqual(faceNormal([1.0, 0.0, -0.0]), [1, 0, -0]);      // V-F-I, east
  assert.deepEqual(faceNormal([-0.0, -1.0, -0.0]), [-0, -1, -0]);  // Y-E-2, forward
});

test("an unreadable face returns null, so the marker is drawn bad", () => {
  for (const bad of ["q+", "", null, undefined, [1, 2], [0, 0, 0], ["a", "b", "c"], {}]) {
    assert.equal(faceNormal(bad), null, `${JSON.stringify(bad)} is not a face`);
  }
});

test("faceLabel renders both forms, and never throws on a vector", () => {
  assert.equal(faceLabel("z-"), "z−");
  // The latent crash: the tooltip called .replace on an array for every vector face.
  assert.equal(faceLabel([0, 0, 1]), "(+0.000, +0.000, +1.000)");
  // An unnamed string shows as itself — the marker is already drawn bad, since
  // faceNormal returns null for it.
  assert.equal(faceLabel("nope"), "nope");
  assert.equal(faceNormal("nope"), null);
  assert.equal(faceLabel([0, 0, 0]), "?");   // a vector with no direction
});

test("every located port in the committed sidecar has a readable face", () => {
  if (!fs.existsSync(SIDECAR)) return;                  // sidecar not built in this tree
  const ports = (JSON.parse(fs.readFileSync(SIDECAR, "utf8")).ports ?? [])
    .filter((p) => Array.isArray(p.pos) && p.pos.length === 3);
  assert.ok(ports.length > 0, "sidecar carries located ports");
  const unreadable = ports.filter((p) => faceNormal(p.face) === null);
  assert.deepEqual(unreadable.map((p) => `${p.component}.${p.name}`), [],
    "every located port's face reads as a direction");
  // The regression would have made these read as [0,0,1]; they must not.
  const vectorFaced = ports.filter((p) => Array.isArray(p.face));
  assert.ok(vectorFaced.length > 0, "the pack still carries vector-faced ports");
});
