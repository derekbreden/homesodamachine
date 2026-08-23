// The drill-down's map, held against the tree it describes
// (contracts/component-sources.js).
//
// Two ways it goes wrong on its own, and one alarm each: an alias naming a file
// that has since moved, and an alias naming a component no assembly carries any
// more. The names come out of the assembly STEPs themselves — occt writes each
// named solid as a PRODUCT entry, and those strings are the `mesh.name` the
// component picker matches a click against.

import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { ALIASES, sourceFileFor } from "../contracts/component-sources.js";
import { walkAssemblies } from "../contracts/parts-tree.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(__dirname, "..", "..");
const HW = path.join(REPO_ROOT, "hardware");

// Every assembly the tree states, nested ones included — an assembly is reached
// by opening the one that holds it, and its own drill-down is checked the same
// way. Taken from the contract rather than restated, so a unit added there is
// covered here without a second edit.
const ASSEMBLIES = walkAssemblies().map((a) => a.model);

function productNames(stepPath) {
  const names = new Set();
  const text = fs.readFileSync(stepPath, "latin1");
  for (const m of text.matchAll(/PRODUCT\s*\(\s*'([^']*)'/g)) names.add(m[1]);
  return names;
}

test("every alias names a file that is there", () => {
  for (const [name, file] of Object.entries(ALIASES)) {
    assert.ok(fs.existsSync(path.join(HW, file)), `${name} -> ${file} (missing)`);
  }
});

test("every alias names a component an assembly carries", (t) => {
  const present = ASSEMBLIES
    .map((rel) => path.join(HW, rel))
    .filter((p) => fs.existsSync(p));
  if (!present.length) return t.skip("assemblies not built");
  const carried = new Set();
  for (const p of present) for (const n of productNames(p)) carried.add(n);
  const orphans = Object.keys(ALIASES).filter((n) => !carried.has(n));
  assert.deepEqual(orphans, [], "aliases for components no assembly carries");
});

test("a name with no alias resolves against its own stem", () => {
  const files = [
    "printed-parts/enclosure/enclosure/enclosure-back-bottom.step",
    "reference/compressor/compressor.step",
  ];
  assert.equal(sourceFileFor("enclosure-back-bottom", files), files[0]);
  assert.equal(sourceFileFor("compressor", files), files[1]);
});

test("an alias beats the stem search, and a body the assembly builds has nowhere to go", () => {
  const files = ["reference/seaflo-22-pump/seaflo-22-pump.step"];
  assert.equal(sourceFileFor("seaflo-pump", files), files[0]);
  assert.equal(sourceFileFor("tube-fluid-17", files), null);
});

test("an alias whose file is gone from the tree reads as nowhere, not as a broken link", () => {
  assert.equal(sourceFileFor("seaflo-pump", []), null);
  assert.equal(sourceFileFor("seaflo-pump", null), null);
  assert.equal(sourceFileFor("", ["a/b.step"]), null);
});
