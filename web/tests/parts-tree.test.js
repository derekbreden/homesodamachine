// The seating /3d browses: two units, the cold core nested inside the enclosure,
// and every other file claimed by the directory an assembly places from, by the
// bought geometry no one unit owns, or by the tooling a bench works from.
//
// Two halves. The first is `seatParts` as a pure function over path lists — the
// folding of a part's representations, the whole leading its directory, every
// model claimed ahead of the directories they share, the tooling claimed ahead of
// the sweep, a child sweeping ahead of its parent. The second walks the real
// hardware tree and asserts nothing in it comes back unseated, which is what
// catches a new part directory the day it lands rather than when someone notices
// it missing from the page.

import { test } from "node:test";
import assert from "node:assert/strict";
import path from "node:path";
import { fileURLToPath } from "node:url";

import {
  ASSEMBLIES, CARD_MODELS, PURCHASED, TOOLING, EXCLUDED_DIRS,
  isWhole, seatParts, walkAssemblies,
} from "../contracts/parts-tree.js";
import { walkFiles } from "../lib/walk.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const HARDWARE = path.resolve(__dirname, "..", "..", "hardware");

const names = (parts) => parts.map((p) => p.name);
const files = (parts) => parts.flatMap((p) => p.kinds.map((k) => k.file));

// Every assembly of a seated tree, outermost first.
const flat = (tree) => {
  const out = [];
  const walk = (nodes) => nodes.forEach((a) => { out.push(a); walk(a.children); });
  walk(tree.assemblies);
  return out;
};
const byId = (tree, id) => flat(tree).find((a) => a.id === id);
// Everything every assembly's own sweep claimed.
const allInside = (tree) => flat(tree).flatMap((a) => a.inside);

test("a part's representations fold into one card", () => {
  const dir = "cut-parts/carbonation/endcaps-circular";
  const tree = seatParts({
    steps: [`${dir}/endcap-circular-2hole.step`],
    dxfs: [`${dir}/endcap-circular-2hole.dxf`],
  });
  const inside = allInside(tree);
  assert.equal(inside.length, 1);
  assert.equal(inside[0].name, "endcap-circular-2hole");
  // The STEP is the richer representation, so it is what the card opens.
  assert.equal(inside[0].primary.type, "step");
  assert.deepEqual(inside[0].kinds.map((k) => k.type), ["step", "dxf"]);
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
  assert.deepEqual(names(allInside(tree)),
    ["enclosure", "enclosure-back-top", "enclosure-front-top"]);
});

test("an assembly's own model is its card, not a part of the directory it shares", () => {
  const tree = seatParts({
    steps: ["manifold-layout/enclosure-assembly.step", "manifold-layout/manifold-layout.step"],
  });
  const enclosure = byId(tree, "enclosure-assembly");
  assert.equal(enclosure.model.name, "enclosure-assembly");
  // The sub-layout the assembly places is reached inside it, not listed.
  assert.deepEqual(names(enclosure.inside), ["manifold-layout"]);
});

test("a nested assembly is a card of its own, and its parts are its own", () => {
  const tree = seatParts({
    steps: ["manifold-layout/enclosure-assembly.step",
            "cold-core-layout/cold-core-assembly.step",
            "printed-parts/cold-core/foam-shell/foam-shell.step"],
  });
  const enclosure = byId(tree, "enclosure-assembly");
  const core = enclosure.children.find((c) => c.id === "cold-core-assembly");

  // The cold core stands under the enclosure and nowhere else.
  assert.ok(core, "the cold core is a child of the enclosure");
  assert.equal(tree.assemblies.length, 2);
  assert.equal(core.model.name, "cold-core-assembly");
  // Its own pieces are claimed by it, not by the unit that holds it.
  assert.deepEqual(names(core.inside), ["foam-shell"]);
  assert.deepEqual(names(enclosure.inside), []);
});

test("purchased geometry is claimed by no one unit", () => {
  const tree = seatParts({ steps: ["reference/worm-clamp/worm-clamp.step"] });
  assert.deepEqual(names(tree.purchased), ["worm-clamp"]);
  assert.deepEqual(names(allInside(tree)), []);
  assert.deepEqual(tree.unseated, []);
});

test("a soft part its host does not seat is claimed with its neighbours", () => {
  const d = "printed-parts/cold-core/reservoir";
  const tree = seatParts({
    steps: [`${d}/reservoir-left.step`, `${d}/reservoir-gasket.step`,
            `${d}/reservoir-retaining-ring.step`],
  });
  const core = byId(tree, "cold-core-assembly");
  assert.deepEqual(names(core.inside),
    ["reservoir-gasket", "reservoir-left", "reservoir-retaining-ring"]);
});

test("tooling comes out of the directory an assembly otherwise sweeps whole", () => {
  const tree = seatParts({
    steps: ["printed-parts/cold-core/coil-mandrel/coil-mandrel.step",
            "printed-parts/cold-core/foam-shell/foam-shell.step"],
    glbs: ["assembly/scenes/glb/back-top.glb"],
  });
  assert.deepEqual(names(tree.tooling), ["back-top", "coil-mandrel"]);
  assert.deepEqual(names(byId(tree, "cold-core-assembly").inside), ["foam-shell"]);
});

test("an excluded directory is not browsed", () => {
  const tree = seatParts({ steps: ["assembly/scenes/out/cold-core.step"] });
  assert.deepEqual(tree.unseated, []);
  assert.deepEqual(tree.tooling, []);
  assert.deepEqual(allInside(tree), []);
});

test("a directory nothing claims comes back unseated", () => {
  const tree = seatParts({ steps: ["printed-parts/somewhere-new/widget/widget.step"] });
  assert.deepEqual(tree.unseated, ["printed-parts/somewhere-new/widget"]);
});

test("every id is unique, and every assembly names a model", () => {
  const ids = walkAssemblies().map((a) => a.id);
  assert.equal(new Set(ids).size, ids.length);
  for (const a of walkAssemblies()) {
    assert.ok(a.model.endsWith(".step"), `${a.id} names no model`);
  }
});

test("the page's cards are the roots, and only the roots", () => {
  // _cadq_export._page_paints reads CARD_MODELS as text and gates every thumbnail
  // this repository writes on it. A nested assembly has no card.
  assert.deepEqual(CARD_MODELS, ASSEMBLIES.map((a) => a.model));
  const nested = walkAssemblies().filter((a) => !ASSEMBLIES.includes(a));
  for (const a of nested) {
    assert.ok(!CARD_MODELS.includes(a.model), `${a.id} is nested and needs no card`);
  }
});

test("nothing in the hardware tree is unseated", (t) => {
  const steps = walkFiles(HARDWARE, ".step");
  const dxfs = walkFiles(HARDWARE, ".dxf");
  const glbs = walkFiles(HARDWARE, ".glb");
  if (!steps.length && !dxfs.length && !glbs.length) return t.skip("hardware tree empty");

  const tree = seatParts({ steps, dxfs, glbs });
  assert.deepEqual(tree.unseated, [],
    `place these in contracts/parts-tree.js: ${tree.unseated.join(", ")}`);

  // Every file is claimed by an assembly's model, by that assembly's own sweep,
  // by the bought geometry, by the tooling, or by EXCLUDED_DIRS — the five paths
  // out of the pool, and nothing may take a sixth.
  const claimed = new Set([
    ...flat(tree).flatMap((a) => (a.model ? a.model.kinds.map((k) => k.file) : [])),
    ...files(allInside(tree)),
    ...files(tree.purchased),
    ...files(tree.tooling),
  ]);
  const excluded = (f) => EXCLUDED_DIRS.some((d) => f === d || f.startsWith(d + "/"));
  for (const f of [...steps, ...dxfs, ...glbs]) {
    assert.ok(claimed.has(f) || excluded(f), `${f} is neither claimed nor excluded`);
  }

  // Every assembly the tree states has its model on this disk.
  for (const a of flat(tree)) assert.ok(a.model, `${a.id} has no model to draw`);
});

test("no two lists claim the same directory", () => {
  const held = walkAssemblies().flatMap((a) => a.holds || []);
  const all = [...held, ...PURCHASED, ...TOOLING];
  assert.equal(new Set(all).size, all.length, "a directory is named twice");

  // Tooling stands inside directories an assembly sweeps; nothing else may.
  const overlaps = (a, b) => a === b || a.startsWith(b + "/") || b.startsWith(a + "/");
  for (const s of PURCHASED) {
    for (const h of held) {
      assert.ok(!overlaps(s, h), `${s} and ${h} overlap`);
    }
  }
});
