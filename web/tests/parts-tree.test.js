// The seating /3d browses: two units, the cold core nested inside the enclosure,
// and every other file claimed by the directory an assembly places from, by the
// bought geometry no one unit owns, or by the tooling a bench works from.
//
// Two halves. The first is `seatParts` as a pure function over path lists — the
// folding of a part's representations, every model claimed ahead of the
// directories they share, the tooling claimed ahead of the sweep, a child
// sweeping ahead of its parent. The second walks the real
// hardware tree and asserts nothing in it comes back unseated, which is what
// catches a new part directory the day it lands rather than when someone notices
// it missing from the page.

import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import {
  ASSEMBLIES, PURCHASED, TOOLING, EXCLUDED_DIRS,
  seatParts, walkAssemblies,
} from "../contracts/parts-tree.js";
import { walkFiles } from "../lib/walk.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const HARDWARE = path.resolve(__dirname, "..", "..", "hardware");

const HW = path.resolve(__dirname, "..", "..", "hardware");
const stepsOnDisk = () => fs.existsSync(path.join(HW, "manifold-layout", "enclosure-assembly.step"));
const readStep = (rel) => {
  const f = path.join(HW, rel);
  return fs.existsSync(f) ? fs.readFileSync(f, "latin1") : null;
};
const productNames = (text) => {
  const out = new Set();
  for (const m of text.matchAll(/PRODUCT\s*\(\s*'([^']*)'/g)) out.add(m[1].replace(/\/\d+$/, ""));
  return out;
};

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

test("a directory's parts come back in one order on every machine", () => {
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

test("the fixtures namespace is tooling without per-fixture seating", () => {
  const tree = seatParts({
    steps: [
      "printed-parts/fixtures/weld-rotator/weld-rotator-assembly.step",
      "printed-parts/fixtures/future-jig/future-jig.step",
    ],
  });
  assert.deepEqual(names(tree.tooling), ["future-jig", "weld-rotator-assembly"]);
  assert.deepEqual(tree.unseated, []);
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

// EXCLUDED_DIRS states where builds put their workings, and .gitignore is what
// actually holds those directories out of the repository. The two are one claim
// written twice, so this fails when they part rather than letting the next
// generator's `out/` surface as an unseated directory nobody can place.
test("EXCLUDED_DIRS is every out/ .gitignore holds under hardware", () => {
  const ignored = new Set();

  // A rule written in the directory it governs: `out/` inside hardware/x/.gitignore.
  const sweep = (dir) => {
    for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
      const full = path.join(dir, e.name);
      if (e.isDirectory()) {
        if (e.name !== "node_modules" && e.name !== ".git") sweep(full);
      } else if (e.name === ".gitignore") {
        const rel = path.relative(HARDWARE, dir);
        for (const line of fs.readFileSync(full, "utf8").split("\n")) {
          if (/^\s*out\/?\s*$/.test(line)) ignored.add(path.join(rel, "out"));
        }
      }
    }
  };
  sweep(HARDWARE);

  // And a rule written at the root, naming the directory by its full path.
  const root = path.resolve(__dirname, "..", "..", ".gitignore");
  for (const line of fs.readFileSync(root, "utf8").split("\n")) {
    const m = /^hardware\/(.*\/out)\/?\s*$/.exec(line.trim());
    if (m) ignored.add(m[1]);
  }

  assert.deepEqual([...ignored].sort(), [...EXCLUDED_DIRS].sort(),
    "contracts/parts-tree.js and .gitignore disagree about where builds put their workings");
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

// A CHILD'S `node` IS THE ONE THING TYING THIS TREE TO THE GEOMETRY. Everything else here is
// about which file belongs to whom; this says the parent's own model really does hold the child
// as a sub-assembly, under that name, with the child's bodies inside it. Without it the page
// could go on describing a shape the STEP stopped having — which is exactly what it did while
// the appliance placed the core as one opaque solid.
test("a nested assembly is a node its parent's model actually holds", { skip: !stepsOnDisk() },
     () => {
  for (const parent of walkAssemblies()) {
    for (const child of parent.children || []) {
      assert.ok(child.node, `${child.id} states no node, so nothing holds it to the model`);
      const text = readStep(parent.model);
      if (!text) continue;
      const names = productNames(text);
      assert.ok(names.has(child.node),
        `${parent.model} has no ${child.node} node — ${child.id} nests in the page and ` +
        `nowhere in the geometry`);
      const inside = [...names].filter((n) => n.startsWith(child.node + "/"));
      assert.ok(inside.length > 0,
        `${parent.model}'s ${child.node} node holds nothing; ${child.id} claims it holds a stack`);
    }
  }
});
