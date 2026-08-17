// Dependency-graph tests for the dev-server / build-all rebuild ordering.
//
// The headline test is a regression for a real, week-long staleness bug: a
// printed part widened (2026-06-08) but the enclosure/assemblies that
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
  isRunnableScript,
  prunedByTrace,
  findGenerateScripts,
  findScriptsConsumingStep,
  findRunnableScriptsTransitivelyImporting,
  affectedBuildOrder,
  buildProducerMap,
  dependencyGraph,
  buildOrder,
} from "../dev-server/deps.js";

const REPO_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..");
const ROOTS = contentRoots(REPO_ROOT);
const rel = (p) => path.relative(REPO_ROOT, p);
const ends = (suffix) => (c) => rel(c).split(path.sep).join("/").endsWith(suffix);

test("the content root is hardware/", () => {
  const names = ROOTS.map((r) => rel(r).split(path.sep).join("/"));
  assert.deepEqual(names, ["hardware"]);
});

test("an edge goes only where a watched run did not open the file", () => {
  // The licence for dropping any scanned edge, held as a rule over the three values it reads
  // rather than against the one graph the tree carries today. A repo-wide sweep cannot hold
  // this: most of what such a sweep flags is the scan never having found the edge at all —
  // `tools/` is no content root, so every generator's traced read of `tools/docgen/__init__.py`
  // is invisible to the scan and was never the pruning's to drop.
  // Under the real root, because what may be dropped is keyed by repo-relative path — a name
  // outside the tree is one the graph cannot be naming.
  const gen = path.join(REPO_ROOT, "hardware/a/gen.py");
  const other = path.join(REPO_ROOT, "hardware/b/other.py");
  const mod = path.join(REPO_ROOT, "hardware/scripts/_mod.py");
  const scanned = [gen, other];
  const traced = (entries) => new Map(entries);

  assert.deepEqual(
    prunedByTrace(scanned, mod, traced([["hardware/a/gen.py", new Set(["hardware/scripts/_mod.py"])],
                                        ["hardware/b/other.py", new Set()]])),
    [gen],
    "a watched run that opened the file keeps its edge; one that did not, loses it",
  );
  assert.deepEqual(
    prunedByTrace(scanned, mod, traced([["hardware/a/gen.py", new Set()]])),
    [other],
    "a generator the graph has no entry for keeps its edge — no entry is no observation",
  );
  assert.deepEqual(
    prunedByTrace(scanned, mod, null),
    scanned,
    "no graph at all keeps every scanned edge",
  );
  assert.deepEqual(
    prunedByTrace(scanned, "/elsewhere/_mod.py",
                  traced([["hardware/a/gen.py", new Set()], ["hardware/b/other.py", new Set()]])),
    scanned,
    "a module outside the repo is nothing the graph names, so nothing it can contradict",
  );
});

test("the pruning holds on the tree it runs against", () => {
  // A scan cannot tell `import enclosure_assembly` inside a function body that runs on every
  // build (enclosure.py's machine_of) from one that breaks a cycle and rarely runs
  // (_back_panel_dimensions:113). Read as source, both make every generator reaching
  // `_materials` an importer of every bought part. graph.json is the other reading.
  //
  // Live against the tree and the real graph, because the thing under test is agreement
  // between the two — a fixture graph would only test the lookup.
  const graph = JSON.parse(
    fs.readFileSync(path.join(REPO_ROOT, "tools", "bazel", "graph.json"), "utf-8"),
  );
  const runnableTracedReaders = (relMod) =>
    Object.entries(graph).filter(
      ([gen, seen]) =>
        gen !== relMod &&
        (seen.reads || []).includes(relMod) &&
        isRunnableScript(path.join(REPO_ROOT, gen)),
    ).map(([gen]) => gen);

  // NOTHING THE TRACE SAW MAY BE PRUNED. That is the whole safety property: an edge goes
  // only where a watched run of that generator positively did not open that file.
  for (const relMod of [
    "hardware/printed-parts/cold-core/reservoir/reservoir.py",
    "hardware/printed-parts/enclosure/port-ring/port_ring.py",
    "hardware/scripts/_materials.py",
  ]) {
    const kept = new Set(
      findRunnableScriptsTransitivelyImporting(path.join(REPO_ROOT, relMod), ROOTS).map((p) =>
        rel(p).split(path.sep).join("/"),
      ),
    );
    for (const gen of runnableTracedReaders(relMod)) {
      assert.ok(kept.has(gen), `${gen} was watched reading ${relMod} and must still rebuild on it`);
    }
  }

  // And the pruning does something: reservoir.py scanned 74 importers before this, against 24
  // traced steps. A number back near the generator count means the trace stopped being read.
  const reservoir = findRunnableScriptsTransitivelyImporting(
    path.join(REPO_ROOT, "hardware/printed-parts/cold-core/reservoir/reservoir.py"),
    ROOTS,
  ).length;
  const generators = findGenerateScripts(ROOTS).length;
  assert.ok(
    reservoir < generators / 2,
    `reservoir.py reaches ${reservoir} of ${generators} generators — the scan's fan-out is back`,
  );

  // A module the graph has no entry for keeps every scanned edge — absence of an observation
  // is not an observation. hardware/scripts holds the tooling, which is no step's generator.
  const untraced = "hardware/scripts/probe.py";
  assert.ok(!(untraced in graph), `${untraced} is traced now — pick another untraced module`);
  assert.ok(
    findRunnableScriptsTransitivelyImporting(path.join(REPO_ROOT, untraced), ROOTS).length >= 0,
    "an untraced module must resolve without throwing",
  );
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
  // A CYCLE IS THE CAUSE THIS TEST KEEPS FINDING, so it is the cause this test names.
  // `orderOf` degrades on one rather than throwing — it returns an order that is not
  // topological and says nothing — so the only surfacing is an out-of-order pair here, and
  // a pair alone does not say which loop put it there. The loop is read off the same map
  // already in hand, so naming it costs nothing and it is what a reader has to find anyway.
  const cycles = [];
  const done = new Set();
  const onStack = new Set();
  const trail = [];
  function walk(node) {
    if (done.has(node)) return;
    if (onStack.has(node)) {
      cycles.push([...trail.slice(trail.indexOf(node)), node].map(rel).join(" -> "));
      return;
    }
    onStack.add(node);
    trail.push(node);
    for (const dep of deps.get(node) || []) walk(dep);
    trail.pop();
    onStack.delete(node);
    done.add(node);
  }
  for (const node of deps.keys()) walk(node);
  const report = [
    bad.length ? `ordering violations:\n${bad.join("\n")}` : "",
    cycles.length ? `cycles (the usual cause):\n${cycles.join("\n")}` : "",
  ].filter(Boolean).join("\n\n");
  assert.equal(bad.length + cycles.length, 0, report);
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
  // beduan_solenoid.py exports its own STEP and is also the module valve_seat.py builds
  // the cap's cradle bosses from; foam_cap.py reaches the valve only through valve_seat,
  // and valve_seat is itself runnable. They build on each other's python, not their .step,
  // so the STEP-load cascade cannot reach them. Stopping at the first runnable would leave
  // foam-cap-lid-top.step stale when the Beduan's corner inset changed; the walk has to
  // recurse past valve_seat even though it runs on its own.
  const beduan = findGenerateScripts(ROOTS).find(ends("beduan-solenoid/beduan_solenoid.py"));
  const deps = findRunnableScriptsTransitivelyImporting(beduan, ROOTS);
  for (const downstream of [
    "valve-seat/valve_seat.py",
    "cold-core/foam-cap/foam_cap.py",
    "manifold-layout/manifold_layout.py",
    "manifold-layout/enclosure_assembly.py",
  ]) {
    assert.ok(
      deps.some(ends(downstream)),
      `expected ${downstream} among beduan_solenoid's transitive dependents; got:\n${deps.map(rel).join("\n")}`,
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

test("a STEP named in a comment is prose, not a load (phantom-edge regression)", () => {
  // A comment in a SHARED module is the costly case: the step it names resolves to every
  // runnable that imports that module, so one sentence becomes an edge per importer, and one
  // pointing back upstream closes a cycle that costs `buildOrder` its topological order.
  //
  // A STRING LITERAL STILL COUNTS, and must: a generator names its own outputs in code and in
  // the `-> x.step` lines it prints, and `buildProducerMap` reads exactly those. That asymmetry
  // is the point of the scanner — blanking strings alongside comments would lose the producer
  // and every edge downstream of it.
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "deps-comment-"));
  try {
    const partDir = path.join(root, "part");
    fs.mkdirSync(partDir);
    // The producer names its own output in a string, the way _cadq_export callers do.
    fs.writeFileSync(
      path.join(partDir, "part.py"),
      'if __name__ == "__main__":\n    export(shape, "part.step")\n',
    );
    fs.writeFileSync(path.join(partDir, "part.step"), "ISO-10303-21;\n");

    // A shared module that only MENTIONS the step, and a runnable that imports it.
    fs.writeFileSync(path.join(root, "_notes.py"), "# TPU gasket per cap (part.step).\nVALUE = 1\n");
    fs.writeFileSync(path.join(root, "importer.py"), 'import _notes\nif __name__ == "__main__":\n    pass\n');

    // A genuine consumer: it loads the step in code.
    fs.writeFileSync(
      path.join(root, "real.py"),
      'if __name__ == "__main__":\n    load("part.step")\n',
    );

    assert.equal(
      path.basename(buildProducerMap([root]).get("part.step") || ""),
      "part.py",
      "a producer names its output in a string literal — stripping must not reach it",
    );

    const consumers = findScriptsConsumingStep("part.step", [root]).map((p) => path.basename(p));
    assert.deepEqual(
      consumers.sort(),
      ["real.py"],
      "a comment naming a step invented an edge (and, through a shared module, one per importer)",
    );
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
});

test("a STEP a selftest reads is a fixture, not a load (phantom-edge regression)", () => {
  // `tools/bazel/trace_inputs.py` watches a module's `__main__` into graph.json and its
  // `selftest` into selftests.json — two records, because a control's reads are not a
  // build's. This orders a build, so it reads the same line.
  //
  // The case that made it: `hardware/scripts/_mesh_payload.py` holds its tessellation against
  // occt-import-js on one reference solid, and `_cadq_export` imports it to write the
  // `.step.mesh` beside every export in the tree. That one fixture was 79 of the graph's 122
  // edges — every generator waiting on the faucet shell.
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "deps-selftest-"));
  try {
    const partDir = path.join(root, "part");
    fs.mkdirSync(partDir);
    fs.writeFileSync(
      path.join(partDir, "part.py"),
      'if __name__ == "__main__":\n    export(shape, "part.step")\n',
    );
    fs.writeFileSync(path.join(partDir, "part.step"), "ISO-10303-21;\n");

    // A shared module whose selftest reads the step — and whose triple-quoted blob holds a
    // line starting at column 0, which must not end the body early.
    fs.writeFileSync(
      path.join(root, "_mesh.py"),
      "VALUE = 1\n\n\n"
        + "def selftest():\n"
        + '    probe = """\ndef not_a_statement():\n    pass\n"""\n'
        + '    ref = HERE / "part.step"\n'
        + "    return check(ref, probe)\n",
    );
    fs.writeFileSync(
      path.join(root, "importer.py"),
      'import _mesh\nif __name__ == "__main__":\n    pass\n',
    );

    // The same module, loading the step in the work its importers call it for. `selftesting`
    // is a name that merely starts with the word — `trace_inputs._selftests` matches
    // `^def selftest\(` down to the paren, and so does the scanner, or the two disagree about
    // which modules are selftests.
    fs.writeFileSync(
      path.join(root, "_routes.py"),
      "def selftesting_helper():\n"
        + '    return load("part.step")\n\n'
        + "def selftest():\n    return 0\n",
    );
    fs.writeFileSync(
      path.join(root, "router.py"),
      'import _routes\nif __name__ == "__main__":\n    pass\n',
    );

    assert.equal(
      path.basename(buildProducerMap([root]).get("part.step") || ""),
      "part.py",
      "the producer names its output outside any selftest — stripping must not reach it",
    );

    const consumers = findScriptsConsumingStep("part.step", [root]).map((p) => path.basename(p));
    assert.deepEqual(
      consumers.sort(),
      ["router.py"],
      "a selftest fixture invented an edge per importer of the module holding it",
    );
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
});

test("a cycle in the STEP-load graph throws rather than dropping a constraint", () => {
  // No order puts every producer before its consumer around a ring, so a DFS that walks
  // over one returns an order with a constraint dropped — and which one depends on the walk
  // order, which is a directory listing. That is a build that is correct or stale by
  // accident, and it is what made this file's own build-order test intermittent.
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "deps-cycle-"));
  try {
    for (const [me, other] of [["a", "b"], ["b", "a"]]) {
      const dir = path.join(root, me);
      fs.mkdirSync(dir);
      fs.writeFileSync(
        path.join(dir, `${me}.py`),
        'if __name__ == "__main__":\n'
          + `    load("${other}.step")\n`
          + `    export(shape, "${me}.step")\n`,
      );
      fs.writeFileSync(path.join(dir, `${me}.step`), "ISO-10303-21;\n");
    }
    assert.throws(
      () => buildOrder([root]),
      (err) =>
        /cycle/.test(err.message) && err.message.includes("a.py") && err.message.includes("b.py"),
      "a cycle must throw, naming the ring to look in",
    );
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
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
