// The seating /3d browses: every file the walkers offer stands in one of the
// machine's three assemblies or on the reference shelf.
//
// Two halves. The first is `seatParts` as a pure function over path lists — the
// folding of a part's representations, the whole leading its directory, the
// branch model claimed ahead of the group sharing its directory. The second
// walks the real hardware tree and asserts nothing in it comes back unseated,
// which is what catches a new part directory the day it lands rather than when
// someone notices it missing from the page.

import { test } from "node:test";
import assert from "node:assert/strict";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { BRANCHES, REFERENCE, EXCLUDED_DIRS, isWhole, seatParts } from "../contracts/parts-tree.js";
import { walkFiles } from "../lib/walk.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const HARDWARE = path.resolve(__dirname, "..", "..", "hardware");

const groupIn = (tree, branchId, groupId) =>
  tree.branches.find((b) => b.id === branchId).groups.find((g) => g.id === groupId);

const names = (group) => group.parts.map((p) => p.name);

test("a part's representations fold into one card", () => {
  const dir = "cut-parts/carbonation/endcaps-circular";
  const tree = seatParts({
    steps: [`${dir}/endcap-circular-2hole.step`],
    dxfs: [`${dir}/endcap-circular-2hole.dxf`],
  });
  const parts = groupIn(tree, "cold-core", "vessel").parts;
  assert.equal(parts.length, 1);
  assert.equal(parts[0].name, "endcap-circular-2hole");
  // The STEP is the richer representation, so it is what the card opens.
  assert.equal(parts[0].primary.type, "step");
  assert.deepEqual(parts[0].kinds.map((k) => k.type), ["step", "dxf"]);
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
  assert.deepEqual(names(groupIn(tree, "enclosure-assembly", "box")),
    ["enclosure", "enclosure-back-top", "enclosure-front-top"]);
});

test("a branch's own model leads the branch, not the group sharing its directory", () => {
  const tree = seatParts({
    steps: ["manifold-layout/enclosure-assembly.step", "manifold-layout/manifold-layout.step"],
  });
  const branch = tree.branches.find((b) => b.id === "enclosure-assembly");
  assert.equal(branch.hero.name, "enclosure-assembly");
  assert.deepEqual(names(groupIn(tree, "enclosure-assembly", "manifold")), ["manifold-layout"]);
});

test("the reference shelf's own model heads it and is not listed twice", () => {
  const tree = seatParts({
    steps: [REFERENCE.model, "reference/worm-clamp/worm-clamp.step"],
  });
  assert.equal(tree.reference.hero.name, "asse1022-assembly");
  assert.deepEqual(names(tree.reference), ["worm-clamp"]);
});

test("a scene stands under the assembly its roots belong to", () => {
  const tree = seatParts({
    glbs: ["assembly/scenes/glb/back-top.glb", "assembly/scenes/glb/cold-core.glb"],
  });
  assert.deepEqual(names(groupIn(tree, "enclosure-assembly", "scenes")), ["back-top"]);
  assert.deepEqual(names(groupIn(tree, "cold-core", "scenes")), ["cold-core"]);
});

test("an excluded directory is not browsed", () => {
  const tree = seatParts({ steps: ["assembly/scenes/out/cold-core.step"] });
  assert.deepEqual(tree.unseated, []);
  const seated = tree.branches.flatMap((b) => b.groups.flatMap((g) => g.parts));
  assert.deepEqual(seated, []);
});

test("a directory no group claims comes back unseated", () => {
  const tree = seatParts({ steps: ["printed-parts/somewhere-new/widget/widget.step"] });
  assert.deepEqual(tree.unseated, ["printed-parts/somewhere-new/widget"]);
});

test("every group id is unique within its branch, and every branch id is unique", () => {
  const ids = [...BRANCHES.map((b) => b.id), REFERENCE.id];
  assert.equal(new Set(ids).size, ids.length);
  for (const b of BRANCHES) {
    const gids = b.groups.map((g) => g.id);
    assert.equal(new Set(gids).size, gids.length, `${b.id} repeats a group id`);
  }
});

test("nothing in the hardware tree is unseated", (t) => {
  const steps = walkFiles(HARDWARE, ".step");
  const dxfs = walkFiles(HARDWARE, ".dxf");
  const glbs = walkFiles(HARDWARE, ".glb");
  if (!steps.length && !dxfs.length && !glbs.length) return t.skip("hardware tree empty");

  const tree = seatParts({ steps, dxfs, glbs });
  assert.deepEqual(tree.unseated, [],
    `add a group in contracts/parts-tree.js for: ${tree.unseated.join(", ")}`);

  // Every file is either seated or named in EXCLUDED_DIRS — the two paths out of
  // the pool, and nothing may take a third.
  const seated = new Set([
    ...tree.branches.flatMap((b) => [
      ...(b.hero ? b.hero.kinds : []),
      ...b.groups.flatMap((g) => g.parts.flatMap((p) => p.kinds)),
    ]),
    ...(tree.reference.hero ? tree.reference.hero.kinds : []),
    ...tree.reference.parts.flatMap((p) => p.kinds),
  ].map((k) => k.file));
  const excluded = (f) => EXCLUDED_DIRS.some((d) => f === d || f.startsWith(d + "/"));
  for (const f of [...steps, ...dxfs, ...glbs]) {
    assert.ok(seated.has(f) || excluded(f), `${f} is neither seated nor excluded`);
  }
});
