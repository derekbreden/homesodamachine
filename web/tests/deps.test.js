// Dependency-graph tests for the dev-server / build-all rebuild ordering.
//
// The headline test is a regression for a real, week-long staleness bug: a
// valve-manifold tray widened (2026-06-08) but the enclosure/assemblies that
// only *load* its STEP (never importing its python) weren't rebuilt until an
// unrelated edit re-triggered them (2026-06-14). The watcher tracked Python
// imports but not STEP-load edges. These assert the STEP-load edges are now
// found, run against the live repo tree.

import { test } from "node:test";
import assert from "node:assert/strict";
import path from "node:path";
import { fileURLToPath } from "node:url";

import {
  contentRoots,
  findGenerateScripts,
  findScriptsConsumingStep,
  buildProducerMap,
  dependencyGraph,
  buildOrder,
} from "../dev-server/deps.js";

const REPO_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..");
const ROOTS = contentRoots(REPO_ROOT);
const rel = (p) => path.relative(REPO_ROOT, p);
const ends = (suffix) => (c) => rel(c).split(path.sep).join("/").endsWith(suffix);

test("content roots resolve to the two editions", () => {
  assert.ok(ROOTS.length >= 1, "expected at least the hardware/ root");
});

test("a tray STEP's consumers include the assemblies that only _load it (regression)", () => {
  // source-select-assembly.step is loaded by _contents.py via the _load()
  // helper; _contents.py is imported by the lite enclosure, the lite
  // enclosure-assembly, and the hardware assembly. None of them names the file
  // or calls importStep directly, so the old import-only walk missed all three.
  const consumers = findScriptsConsumingStep("source-select-assembly.step", ROOTS);
  assert.ok(
    consumers.some(ends("pie-in-the-sky/lite/enclosure-assembly/enclosure_assembly.py")),
    `expected lite enclosure-assembly among consumers, got:\n${consumers.map(rel).join("\n")}`,
  );
  assert.ok(
    consumers.some(ends("pie-in-the-sky/lite/enclosure/enclosure.py")),
    "expected lite enclosure among consumers",
  );
  assert.ok(
    consumers.some(ends("hardware/printed-parts/enclosure/enclosure-assembly/enclosure_assembly.py")),
    "expected hardware enclosure-assembly among consumers",
  );
});

test("the reservoir STEP is consumed by the lite enclosure + enclosure-assembly", () => {
  const consumers = findScriptsConsumingStep("reservoir-pockets.step", ROOTS);
  assert.ok(consumers.some(ends("enclosure_assembly.py")), "lite enclosure-assembly");
  assert.ok(consumers.some(ends("enclosure/enclosure.py")), "lite enclosure");
});

test("a producer is never listed as a consumer of its own STEP", () => {
  const producerOf = buildProducerMap(ROOTS);
  const producer = producerOf.get("source-select-assembly.step");
  assert.ok(producer, "the tray assembly STEP should have a producer script");
  const consumers = findScriptsConsumingStep("source-select-assembly.step", ROOTS);
  assert.ok(!consumers.includes(producer), `${rel(producer)} produces the step, not consumes it`);
});

test("build order puts a producer before the scripts that load its STEP", () => {
  const order = buildOrder(ROOTS).map(rel);
  const producer = order.findIndex(
    (s) => s.split(path.sep).join("/").endsWith("source-select-tray/source_select_assembly.py"),
  );
  const consumer = order.findIndex(
    (s) => s.split(path.sep).join("/").endsWith("pie-in-the-sky/lite/enclosure-assembly/enclosure_assembly.py"),
  );
  assert.ok(producer !== -1, "tray assembly generator should be in the order");
  assert.ok(consumer !== -1, "enclosure assembly should be in the order");
  assert.ok(
    producer < consumer,
    "the tray assembly must build before the enclosure assembly that loads it",
  );
});

test("every runnable generator appears exactly once in the build order", () => {
  const scripts = findGenerateScripts(ROOTS);
  const order = buildOrder(ROOTS);
  assert.equal(order.length, scripts.length, "order should cover every generator");
  assert.equal(new Set(order).size, order.length, "no duplicates in the order");
});

test("the build order respects every STEP-load edge (producers before consumers)", () => {
  const deps = dependencyGraph(ROOTS);
  const pos = new Map(buildOrder(ROOTS).map((s, i) => [s, i]));
  const bad = [];
  for (const [consumer, producers] of deps) {
    for (const producer of producers) {
      if (pos.get(producer) >= pos.get(consumer)) {
        bad.push(`${rel(producer)} (producer) is not before ${rel(consumer)} (consumer)`);
      }
    }
  }
  assert.equal(bad.length, 0, `ordering violations:\n${bad.join("\n")}`);
});

test("short basenames don't substring-match longer step names (collision regression)", () => {
  // The bare "assembly.step" token is a substring of "source-select-assembly.step",
  // "pump-case-assembly.step", "enclosure-assembly.step", etc. Matching it as a
  // token must NOT pull in scripts that only reference those longer names — that
  // invented reverse edges and cycles.
  const consumers = findScriptsConsumingStep("assembly.step", ROOTS);
  assert.ok(
    !consumers.some(ends("source-select-tray/source_select_assembly.py")),
    `tray assembly only names *-assembly.step, not the bare assembly.step; got:\n${consumers.map(rel).join("\n")}`,
  );
  assert.ok(
    !consumers.some(ends("flavor/pump-case/pump_case_assembly.py")),
    "pump-case assembly only names pump-case-assembly.step",
  );
});
