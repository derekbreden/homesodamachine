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
import fs from "node:fs";
import os from "node:os";
import { fileURLToPath } from "node:url";

import {
  contentRoots,
  findGenerateScripts,
  findScriptsConsumingStep,
  findRunnableScriptsTransitivelyImporting,
  affectedBuildOrder,
  buildProducerMap,
  dependencyGraph,
  buildOrder,
} from "../dev-server/deps.js";
import { EDITIONS } from "../lib/editions.js";

const REPO_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..");
const ROOTS = contentRoots(REPO_ROOT);
const rel = (p) => path.relative(REPO_ROOT, p);
const ends = (suffix) => (c) => rel(c).split(path.sep).join("/").endsWith(suffix);

test("content roots resolve to the declared editions", () => {
  assert.ok(ROOTS.length >= 1, "expected at least the hardware/ root");
  const names = ROOTS.map((r) => rel(r).split(path.sep).join("/"));
  for (const e of EDITIONS) {
    const dir = e.dir.join("/");
    assert.ok(names.includes(dir), `editions.js declares ${e.id} (${dir}) but it is not a content root`);
  }
});

test("a full-copy edition rebuilds only itself (thin isolation)", () => {
  // thin/hardware/ is a complete copy of hardware/ — every module name exists
  // in both. Without the sibling/edition narrowing in the import walk, one
  // _contents.py edit would rebuild BOTH machines' enclosures on every save.
  // It also has its own hardware/scripts, so even the otherwise-shared
  // _cadq_export resolves per-tree and must not cross.
  const thin = path.join(REPO_ROOT, "thin");
  if (!fs.existsSync(thin)) return; // edition not present in this checkout

  const contents = (root) => path.join(
    root, "printed-parts", "enclosure", "enclosure-assembly", "_contents.py");
  const where = (p) => (rel(p).split(path.sep).join("/").startsWith("thin/") ? "thin" : "kitchen");

  for (const [edition, root] of [
    ["kitchen", path.join(REPO_ROOT, "hardware")],
    ["thin", path.join(thin, "hardware")],
  ]) {
    const deps = findRunnableScriptsTransitivelyImporting(contents(root), ROOTS);
    assert.ok(deps.length > 0, `${edition} _contents.py should rebuild its own assembly`);
    const strays = deps.filter((d) => where(d) !== edition).map(rel);
    assert.deepEqual(strays, [], `a ${edition} _contents.py edit reached another edition`);
  }

  // _cadq_export is the module every generator in a tree imports, and each tree
  // carries its own. So it is the widest test of the narrowing: an edit to one
  // edition's copy must reach that edition's whole build and none of the other's.
  for (const [edition, scripts] of [
    ["kitchen", path.join(REPO_ROOT, "hardware", "scripts", "_cadq_export.py")],
    ["thin", path.join(thin, "hardware", "scripts", "_cadq_export.py")],
  ]) {
    const reach = findRunnableScriptsTransitivelyImporting(scripts, ROOTS).map(where);
    assert.ok(reach.includes(edition), `expected ${edition} generators`);
    assert.deepEqual(
      [...new Set(reach)], [edition],
      `${edition}'s _cadq_export reached another edition`,
    );
  }
});

test("a tray STEP's consumers include the assemblies that only _load it (regression)", () => {
  // source-select-assembly.step is loaded by _contents.py via the _load()
  // helper; _contents.py is imported by the enclosure and the enclosure-assembly.
  // Neither names the file or calls importStep directly, so the old import-only
  // walk missed both.
  const consumers = findScriptsConsumingStep("source-select-assembly.step", ROOTS);
  assert.ok(
    consumers.some(ends("hardware/printed-parts/enclosure/enclosure-assembly/enclosure_assembly.py")),
    `expected the enclosure-assembly among consumers, got:\n${consumers.map(rel).join("\n")}`,
  );
  assert.ok(
    consumers.some(ends("hardware/printed-parts/enclosure/enclosure/enclosure.py")),
    "expected the enclosure among consumers",
  );
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
    (s) => s.split(path.sep).join("/").endsWith("hardware/printed-parts/enclosure/enclosure-assembly/enclosure_assembly.py"),
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

test("the import walk continues THROUGH a generator that doubles as a base module (regression)", () => {
  // single_tray is imported by bag_circuit_tray, which is itself imported by
  // bag_circuit_assembly / nozzle_gate_tray / source_select_tray (they build on
  // the tray's python, not its .step — so the STEP-load cascade can't catch
  // them), and nozzle_gate_tray is in turn imported by nozzle_gate_assembly.
  // Stopping the walk at the first runnable would leave nozzle-gate-tray.step
  // stale when single_tray changed; the walk must recurse past bag_circuit_tray
  // (and then past nozzle_gate_tray) even though both are runnable generators.
  const singleTray = findGenerateScripts(ROOTS).find(ends("single-tray/single_tray.py"));
  const deps = findRunnableScriptsTransitivelyImporting(singleTray, ROOTS);
  for (const downstream of [
    "bag-circuit-tray/bag_circuit_tray.py",
    "bag-circuit-tray/bag_circuit_assembly.py",
    "nozzle-gate-tray/nozzle_gate_tray.py",
    "nozzle-gate-tray/nozzle_gate_assembly.py",
    "source-select-tray/source_select_tray.py",
  ]) {
    assert.ok(
      deps.some(ends(downstream)),
      `expected ${downstream} among single_tray's transitive dependents; got:\n${deps.map(rel).join("\n")}`,
    );
  }
});

test("an edition's module does not drag in the other edition's twin (regression)", () => {
  // hardware/ and thin/hardware/ mirror each other's filenames — _contents.py,
  // enclosure.py, enclosure_assembly.py, scorecard.py. Matching dependents by bare
  // module name rebuilt the OTHER machine's assembly for a _contents.py edit it never
  // imports: a second full assembly competing for the same cores on every route edit,
  // which is most of what made a build take minutes.
  const hwContents = path.join(
    REPO_ROOT, "hardware", "printed-parts", "enclosure", "enclosure-assembly", "_contents.py");
  const deps = findRunnableScriptsTransitivelyImporting(hwContents, ROOTS).map(rel);
  assert.ok(
    deps.some(ends("enclosure/enclosure-assembly/enclosure_assembly.py")),
    `hardware's own assembly must still rebuild; got:\n${deps.join("\n")}`,
  );
  assert.ok(
    !deps.some((d) => d.split(path.sep).join("/").startsWith("thin/")),
    `no thin script may rebuild for a hardware _contents.py edit; got:\n${deps.join("\n")}`,
  );
});

test("affectedBuildOrder: one edit's wave lists each script once, seeds first, producers before consumers", () => {
  // Seed the wave the way the watcher does for a single_tray edit: the file plus
  // every runnable that transitively imports it.
  const single = findGenerateScripts(ROOTS).find(ends("single-tray/single_tray.py"));
  const seeds = [single, ...findRunnableScriptsTransitivelyImporting(single, ROOTS).filter((s) => s !== single)];
  const { order, loadsOf } = affectedBuildOrder(seeds, ROOTS);
  const seedSet = new Set(seeds);

  // Run-once: no script appears twice (the old recursive cascade re-ran a shared
  // consumer once per producer).
  assert.equal(order.length, new Set(order).size, "a script is listed more than once");

  // Every seed is present, and every seed precedes every non-seed (the parts
  // being edited rebuild before the heavy downstream that only loads them).
  for (const s of seeds) assert.ok(order.includes(s), `seed missing from order: ${rel(s)}`);
  const lastSeed = order.reduce((m, s, i) => (seedSet.has(s) ? i : m), -1);
  const firstNonSeed = order.findIndex((s) => !seedSet.has(s));
  assert.ok(firstNonSeed === -1 || lastSeed < firstNonSeed, "a non-seed is ordered before a seed");

  // The enclosure loads all four tray assemblies, yet appears exactly once.
  const encl = order.filter(ends("hardware/printed-parts/enclosure/enclosure-assembly/enclosure_assembly.py"));
  assert.equal(encl.length, 1, "hardware enclosure-assembly should appear exactly once");

  // Producer before consumer over a real STEP-load edge: enclosure_assembly loads
  // enclosure.step, so enclosure.py must be built first.
  const idx = (suffix) => order.findIndex(ends(suffix));
  const enclosure = idx("hardware/printed-parts/enclosure/enclosure/enclosure.py");
  const enclosureAssembly = idx("hardware/printed-parts/enclosure/enclosure-assembly/enclosure_assembly.py");
  if (enclosure !== -1 && enclosureAssembly !== -1) {
    assert.ok(enclosure < enclosureAssembly, "enclosure.py must precede the enclosure-assembly that loads its STEP");
  }
});

test("the per-call memo does not outlive its call (staleness regression)", () => {
  // The graph functions cache walks, source reads and sub-results for the
  // duration of one top-level call — the same file is read dozens of times
  // inside nested loops. The cache is torn down on the way out, so the next
  // call after an edit reads the edit. If it ever leaked across calls the
  // watcher would answer every rebuild from the tree as it stood at boot.
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "deps-memo-"));
  try {
    const mod = path.join(root, "_shared.py");
    const gen = path.join(root, "widget.py");
    fs.writeFileSync(mod, "VALUE = 1\n");
    fs.writeFileSync(gen, 'if __name__ == "__main__":\n    pass\n');

    // Nothing imports the module yet.
    assert.deepEqual(findRunnableScriptsTransitivelyImporting(mod, [root]), []);

    // Add the import; the very next call must see it.
    fs.writeFileSync(gen, 'import _shared\nif __name__ == "__main__":\n    pass\n');
    assert.deepEqual(
      findRunnableScriptsTransitivelyImporting(mod, [root]).map((p) => path.basename(p)),
      ["widget.py"],
      "a cached walk survived its call and hid a new import edge",
    );

    // A new file on disk must show up too — the directory walk is cached as well.
    fs.writeFileSync(path.join(root, "gadget.py"), 'import _shared\nif __name__ == "__main__":\n    pass\n');
    assert.equal(
      findRunnableScriptsTransitivelyImporting(mod, [root]).length, 2,
      "a cached directory walk survived its call and hid a new file",
    );
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
});
