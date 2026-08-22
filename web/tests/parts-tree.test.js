// The seating /3d browses: three assemblies, a shelf of what none of them
// places, and every other file claimed by the directory an assembly places from.
//
// Two halves. The first is `seatParts` as a pure function over path lists — the
// folding of a part's representations, the whole leading its directory, the
// assembly's model claimed ahead of the directory it shares, the shelf claimed
// ahead of the sweep. The second walks the real hardware tree and asserts nothing
// in it comes back unseated, which is what catches a new part directory the day it
// lands rather than when someone notices it missing from the page.

import { test } from "node:test";
import assert from "node:assert/strict";
import path from "node:path";
import { fileURLToPath } from "node:url";

import {
  ASSEMBLIES, LOOSE, INSIDE_DIRS, EXCLUDED_DIRS, isWhole, seatParts,
} from "../contracts/parts-tree.js";
import { walkFiles } from "../lib/walk.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const HARDWARE = path.resolve(__dirname, "..", "..", "hardware");

const names = (parts) => parts.map((p) => p.name);
const files = (parts) => parts.flatMap((p) => p.kinds.map((k) => k.file));

test("a part's representations fold into one card", () => {
  const dir = "cut-parts/carbonation/endcaps-circular";
  const tree = seatParts({
    steps: [`${dir}/endcap-circular-2hole.step`],
    dxfs: [`${dir}/endcap-circular-2hole.dxf`],
  });
  assert.equal(tree.inside.length, 1);
  assert.equal(tree.inside[0].name, "endcap-circular-2hole");
  // The STEP is the richer representation, so it is what the card opens.
  assert.equal(tree.inside[0].primary.type, "step");
  assert.deepEqual(tree.inside[0].kinds.map((k) => k.type), ["step", "dxf"]);
});

test("the whole of a directory leads it", () => {
  assert.ok(isWhole("printed-parts/cold-core/foam-shell/foam-shell.step"));
  assert.ok(isWhole("printed-parts/electronics/pcba-tray/pcba-assembly.step"));
  assert.ok(!isWhole("printed-parts/cold-core/foam-cap/foam-cap-top.step"));

  const d = "printed-parts/enclosure/enclosure";
  const tree = seatParts({
    steps: [`${d}/enclosure-front-top.step`, `${d}/enclosure.step`,
            `${d}/enclosure-back-top.step`],
  });
  assert.deepEqual(names(tree.inside),
    ["enclosure", "enclosure-back-top", "enclosure-front-top"]);
});

test("an assembly's own model is its card, not a part of the directory it shares", () => {
  const tree = seatParts({
    steps: ["manifold-layout/enclosure-assembly.step", "manifold-layout/manifold-layout.step"],
  });
  const enclosure = tree.assemblies.find((a) => a.id === "enclosure-assembly");
  assert.equal(enclosure.model.name, "enclosure-assembly");
  // The sub-layout the assembly places is reached inside it, not listed.
  assert.deepEqual(names(tree.inside), ["manifold-layout"]);
  assert.deepEqual(tree.loose.parts, []);
});

test("purchased geometry is reached inside an assembly, not listed", () => {
  const tree = seatParts({ steps: ["reference/worm-clamp/worm-clamp.step"] });
  assert.deepEqual(names(tree.inside), ["worm-clamp"]);
  assert.deepEqual(tree.loose.parts, []);
  assert.deepEqual(tree.unseated, []);
});

test("a soft part its host does not seat stands on the shelf; its neighbours do not", () => {
  const d = "printed-parts/cold-core/reservoir";
  const tree = seatParts({
    steps: [`${d}/reservoir-left.step`, `${d}/reservoir-gasket.step`,
            `${d}/reservoir-retaining-ring.step`, `${d}/reservoir-bulkhead-seal-dry.step`],
  });
  assert.deepEqual(names(tree.loose.parts),
    ["reservoir-bulkhead-seal-dry", "reservoir-gasket", "reservoir-retaining-ring"]);
  assert.deepEqual(names(tree.inside), ["reservoir-left"]);
});

test("a bench scene stands on the shelf", () => {
  const tree = seatParts({
    glbs: ["assembly/scenes/glb/back-top.glb", "assembly/scenes/glb/cold-core.glb"],
  });
  assert.deepEqual(names(tree.loose.parts), ["back-top", "cold-core"]);
});

test("an excluded directory is not browsed", () => {
  const tree = seatParts({ steps: ["assembly/scenes/out/cold-core.step"] });
  assert.deepEqual(tree.unseated, []);
  assert.deepEqual(tree.loose.parts, []);
  assert.deepEqual(tree.inside, []);
});

test("a directory nothing claims comes back unseated", () => {
  const tree = seatParts({ steps: ["printed-parts/somewhere-new/widget/widget.step"] });
  assert.deepEqual(tree.unseated, ["printed-parts/somewhere-new/widget"]);
});

test("every id is unique, and every assembly names a model", () => {
  const ids = [...ASSEMBLIES.map((a) => a.id), LOOSE.id];
  assert.equal(new Set(ids).size, ids.length);
  for (const a of ASSEMBLIES) assert.ok(a.model.endsWith(".step"), `${a.id} names no model`);
});

test("nothing in the hardware tree is unseated", (t) => {
  const steps = walkFiles(HARDWARE, ".step");
  const dxfs = walkFiles(HARDWARE, ".dxf");
  const glbs = walkFiles(HARDWARE, ".glb");
  if (!steps.length && !dxfs.length && !glbs.length) return t.skip("hardware tree empty");

  const tree = seatParts({ steps, dxfs, glbs });
  assert.deepEqual(tree.unseated, [],
    `place these in contracts/parts-tree.js: ${tree.unseated.join(", ")}`);

  // Every file is claimed by an assembly's model, by the shelf, by the sweep of
  // the directories the assemblies place from, or by EXCLUDED_DIRS — the four
  // paths out of the pool, and nothing may take a fifth.
  const claimed = new Set([
    ...tree.assemblies.flatMap((a) => (a.model ? a.model.kinds.map((k) => k.file) : [])),
    ...files(tree.loose.parts),
    ...files(tree.inside),
  ]);
  const excluded = (f) => EXCLUDED_DIRS.some((d) => f === d || f.startsWith(d + "/"));
  for (const f of [...steps, ...dxfs, ...glbs]) {
    assert.ok(claimed.has(f) || excluded(f), `${f} is neither claimed nor excluded`);
  }

  // Every assembly the page draws has its model on this disk.
  for (const a of tree.assemblies) assert.ok(a.model, `${a.id} has no model to draw`);
});

test("the shelf and the sweep claim disjoint sets", () => {
  const overlap = LOOSE.holds.filter((h) => INSIDE_DIRS.includes(h));
  assert.deepEqual(overlap, []);
});
