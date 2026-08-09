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

test("the enclosure assembly rebuilds on every module that draws it", () => {
  // enclosure_assembly.py IS the enclosure assembly: it places every body and sizes the box
  // around them. The modules beside it author the runs between those bodies and grade
  // the result, and hardware/scripts holds the export helper every generator imports.
  // An edit to any of them has to reach the generator, or the .step, the elevations
  // and the scorecard sidecar on disk stop matching the source that drew them.
  const assembly = "manifold-layout/enclosure_assembly.py";
  assert.ok(
    findGenerateScripts(ROOTS).some(ends(assembly)),
    "the enclosure assembly must be a runnable generator, or nothing rebuilds it at all",
  );

  for (const mod of ["hardware/manifold-layout/_lines.py",
    "hardware/manifold-layout/_scorecard.py",
    "hardware/scripts/_cadq_export.py"]) {
    const full = path.join(REPO_ROOT, ...mod.split("/"));
    assert.ok(fs.existsSync(full), `${mod} exists`);
    const deps = findRunnableScriptsTransitivelyImporting(full, ROOTS).map(rel);
    assert.ok(
      deps.some(ends(assembly)),
      `an edit to ${mod} must rebuild the assembly; got:\n${deps.join("\n")}`,
    );
  }
});

test("a part's STEP consumers include the assembly that only _loads it (regression)", () => {
  // enclosure_assembly.py names each of these in a path constant and hands the path to
  // importStep — the edge is a string, not an import, so an import-only walk finds
  // none of them. The Wago is the case with nothing else to fall back on: the lever nut
  // is placed ten times off its reference STEPs and no script imports the module. All
  // three sizes are listed because the scan reads literal text: a path built from a size
  // at runtime is one no filename appears in, and the edge goes quiet without failing.
  for (const step of ["foam-assembly.step", "seaflo-22-pump.step",
                      "wago-221-413.step", "wago-221-415.step", "wago-221-420.step"]) {
    const consumers = findScriptsConsumingStep(step, ROOTS);
    assert.ok(
      consumers.some(ends("hardware/manifold-layout/enclosure_assembly.py")),
      `expected enclosure_assembly among ${step} consumers, got:\n`
      + consumers.map(rel).join("\n"),
    );
  }
});

test("a producer is never listed as a consumer of its own STEP", () => {
  const producerOf = buildProducerMap(ROOTS);
  const producer = producerOf.get("foam-assembly.step");
  assert.ok(producer, "the foam assembly STEP should have a producer script");
  const consumers = findScriptsConsumingStep("foam-assembly.step", ROOTS);
  assert.ok(!consumers.includes(producer), `${rel(producer)} produces the step, not consumes it`);
});

test("build order puts a producer before the scripts that load its STEP", () => {
  const order = buildOrder(ROOTS).map(rel);
  const producer = order.findIndex(
    (s) => s.split(path.sep).join("/").endsWith("cold-core/foam-assembly/foam_assembly.py"),
  );
  const consumer = order.findIndex(
    (s) => s.split(path.sep).join("/").endsWith("hardware/manifold-layout/enclosure_assembly.py"),
  );
  assert.ok(producer !== -1, "foam assembly generator should be in the order");
  assert.ok(consumer !== -1, "enclosure_assembly should be in the order");
  assert.ok(
    producer < consumer,
    "the foam assembly must build before the enclosure assembly that loads it",
  );
});

test("a tool that requires an argument is not a generator (regression)", () => {
  // `build-all` spawns every generator bare. A script whose entry point demands a positional
  // has nothing to do that way, so it failed on every run — two of them, on every build, for
  // as long as they have sat beside the board they query. An OPTIONAL positional is a
  // different thing: board-3d.py defaults its `target` to the board in its own directory and
  // is a real generator, so the rule must keep it.
  const scripts = findGenerateScripts(ROOTS).map((s) => rel(s).split(path.sep).join("/"));
  for (const tool of ["hardware/pcb/pcba/topreach.py", "hardware/pcb/pcba/trace-check.py"]) {
    assert.ok(!scripts.includes(tool), `${tool} requires arguments and must not be spawned bare`);
  }
  assert.ok(
    scripts.includes("hardware/pcb/pcba/board-3d.py"),
    "board-3d.py's positional is optional — it must stay a generator",
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
  // "pump-case-assembly.step", "foam-assembly.step", etc. Matching it as a
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
  // single_tray is imported by each N-valve tray, and each of those by its own
  // assembly — they build on the tray's python, not its .step, so the STEP-load
  // cascade cannot reach them. Stopping at the first runnable would leave
  // two-valve-assembly.step stale when single_tray changed; the walk has to recurse
  // past two_valve_tray even though it is itself a runnable generator.
  const singleTray = findGenerateScripts(ROOTS).find(ends("single-tray/single_tray.py"));
  const deps = findRunnableScriptsTransitivelyImporting(singleTray, ROOTS);
  for (const downstream of [
    "two-valve-tray/two_valve_tray.py",
    "two-valve-tray/two_valve_assembly.py",
    "single-valve-tray/single_valve_tray.py",
    "single-valve-tray/single_valve_assembly.py",
  ]) {
    assert.ok(
      deps.some(ends(downstream)),
      `expected ${downstream} among single_tray's transitive dependents; got:\n${deps.map(rel).join("\n")}`,
    );
  }
});

test("a manifold_layout edit rebuilds the assembly that imports it", () => {
  // enclosure_assembly.py imports manifold_layout as a module, not as a STEP, so the wave
  // that rebuilds it comes from the import walk rather than the STEP-load cascade.
  const ml = path.join(REPO_ROOT, "hardware", "manifold-layout", "manifold_layout.py");
  const deps = findRunnableScriptsTransitivelyImporting(ml, ROOTS).map(rel);
  assert.ok(
    deps.some(ends("manifold-layout/enclosure_assembly.py")),
    `the enclosure assembly must rebuild; got:\n${deps.join("\n")}`,
  );
});

test("affectedBuildOrder: one edit's wave lists each script once, seeds first, producers before consumers", () => {
  // Seed the wave the way the watcher does for a foam_assembly edit: the file
  // plus every runnable that transitively imports it.
  const foam = findGenerateScripts(ROOTS).find(ends("cold-core/foam-assembly/foam_assembly.py"));
  const seeds = [foam, ...findRunnableScriptsTransitivelyImporting(foam, ROOTS).filter((s) => s !== foam)];
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

  // enclosure_assembly arrives twice — it imports foam_assembly's python AND loads
  // foam-assembly.step — yet appears exactly once.
  const fh = order.filter(ends("hardware/manifold-layout/enclosure_assembly.py"));
  assert.equal(fh.length, 1, "enclosure_assembly should appear exactly once");

  // Producer before consumer over a real STEP-load edge: enclosure_assembly loads
  // foam-assembly.step, so foam_assembly.py must be built first.
  const idx = (suffix) => order.findIndex(ends(suffix));
  const producer = idx("cold-core/foam-assembly/foam_assembly.py");
  const enclosureAssembly = idx("hardware/manifold-layout/enclosure_assembly.py");
  if (producer !== -1 && enclosureAssembly !== -1) {
    assert.ok(producer < enclosureAssembly,
      "foam_assembly.py must precede the enclosure assembly that loads its STEP");
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

test("a `.retired` directory is out of the graph, and its subdirectories with it", () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "deps-retired-"));
  try {
    const live = path.join(root, "live");
    const retired = path.join(root, "retired");
    const nested = path.join(retired, "attempt");
    fs.mkdirSync(live);
    fs.mkdirSync(nested, { recursive: true });

    const shared = path.join(root, "_shared.py");
    fs.writeFileSync(shared, "VALUE = 1\n");
    const gen = 'import _shared\nif __name__ == "__main__":\n    pass\n';
    fs.writeFileSync(path.join(live, "widget.py"), gen);
    fs.writeFileSync(path.join(retired, "old.py"), gen);
    fs.writeFileSync(path.join(nested, "older.py"), gen);
    // The producer edge: a runnable beside the .step whose source names it.
    fs.writeFileSync(path.join(retired, "old.step"), "ISO-10303-21;\n");

    assert.deepEqual(
      findGenerateScripts([root]).map((p) => path.basename(p)).sort(),
      ["old.py", "older.py", "widget.py"],
      "precondition: all three are runnables before the marker goes down",
    );

    fs.writeFileSync(path.join(retired, ".retired"), "kept for reading\n");

    assert.deepEqual(
      findGenerateScripts([root]).map((p) => path.basename(p)),
      ["widget.py"],
      "a retired directory still offered generators to build",
    );
    assert.deepEqual(
      findRunnableScriptsTransitivelyImporting(shared, [root]).map((p) => path.basename(p)),
      ["widget.py"],
      "an edit upstream of a retired tree still rebuilt into it",
    );
    assert.equal(
      buildProducerMap([root]).has("old.step"), false,
      "a retired .step still claimed a producer",
    );
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
});
